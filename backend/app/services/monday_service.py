from pathlib import Path
import pandas as pd
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import get_settings


class MondayServiceBase:
    async def fetch_deals(self) -> pd.DataFrame:
        raise NotImplementedError

    async def fetch_work_orders(self) -> pd.DataFrame:
        raise NotImplementedError


class MondayMockClient(MondayServiceBase):
    async def fetch_deals(self) -> pd.DataFrame:
        settings = get_settings()
        csv_path = Path(settings.DATA_DIR) / 'deals.csv'
        if not csv_path.exists():
            csv_path = Path(__file__).parent.parent.parent.parent / 'data' / 'deals.csv'
        try:
            df = pd.read_csv(csv_path)
            df = df[df['Deal Status'] != 'Deal Status'].copy()
            return df
        except Exception as e:
            print(f"[Mock] Error fetching deals: {e}")
            return pd.DataFrame()

    async def fetch_work_orders(self) -> pd.DataFrame:
        settings = get_settings()
        csv_path = Path(settings.DATA_DIR) / 'work_orders.csv'
        if not csv_path.exists():
            csv_path = Path(__file__).parent.parent.parent.parent / 'data' / 'work_orders.csv'
        try:
            df = pd.read_csv(csv_path, skiprows=1)
            return df
        except Exception as e:
            print(f"[Mock] Error fetching work orders: {e}")
            return pd.DataFrame()


class MondayGraphQLClient(MondayServiceBase):
    MONDAY_API_URL = 'https://api.monday.com/v2'

    # Query 1: get column id→title mapping
    _COLS_QUERY = """
    query ($board: ID!) {
        boards(ids: [$board]) {
            name
            columns { id title type }
        }
    }
    """

    # Query 2: paginate items (column_values WITHOUT title field — not supported)
    _ITEMS_QUERY = """
    query ($board: ID!, $cursor: String) {
        boards(ids: [$board]) {
            items_page(limit: 100, cursor: $cursor) {
                cursor
                items {
                    id
                    name
                    column_values { id text value }
                }
            }
        }
    }
    """

    def _headers(self, settings) -> dict:
        return {
            "Authorization": settings.MONDAY_API_KEY,
            "API-Version": "2023-10",
            "Content-Type": "application/json",
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _fetch_board_data(self, board_id: str) -> pd.DataFrame:
        settings = get_settings()
        headers = self._headers(settings)

        async with httpx.AsyncClient(timeout=30) as client:
            # ── Step 1: fetch column id→title map ──────────────────────────
            r = await client.post(
                self.MONDAY_API_URL,
                json={"query": self._COLS_QUERY, "variables": {"board": board_id}},
                headers=headers,
            )
            r.raise_for_status()
            col_data = r.json()
            if "errors" in col_data:
                raise Exception(f"Monday API column error: {col_data['errors']}")

            board_info = col_data["data"]["boards"][0]
            col_map = {c["id"]: c["title"] for c in board_info["columns"]}
            print(f"[Monday] Board '{board_info['name']}' — {len(col_map)} columns fetched")

            # ── Step 2: paginate all items ──────────────────────────────────
            all_items = []
            cursor = None

            while True:
                variables: dict = {"board": board_id}
                if cursor:
                    variables["cursor"] = cursor

                r2 = await client.post(
                    self.MONDAY_API_URL,
                    json={"query": self._ITEMS_QUERY, "variables": variables},
                    headers=headers,
                )
                r2.raise_for_status()
                item_data = r2.json()
                if "errors" in item_data:
                    raise Exception(f"Monday API item error: {item_data['errors']}")

                page = item_data["data"]["boards"][0]["items_page"]
                page_items = page["items"]

                for item in page_items:
                    row: dict = {"Deal name masked": item["name"],
                                 "Deal Name": item["name"]}   # alias for both boards
                    for cv in item["column_values"]:
                        col_title = col_map.get(cv["id"], cv["id"])
                        row[col_title] = cv["text"] if cv["text"] else None
                    all_items.append(row)

                cursor = page.get("cursor")
                if not cursor:
                    break

            print(f"[Monday] Fetched {len(all_items)} items from board '{board_info['name']}'")
            return pd.DataFrame(all_items)

    async def fetch_deals(self) -> pd.DataFrame:
        settings = get_settings()
        try:
            df = await self._fetch_board_data(settings.DEALS_BOARD_ID)
            # The item name IS the Deal Name in monday.com
            if "Name" in df.columns and "Deal Name" not in df.columns:
                df["Deal Name"] = df["Name"]
            return df
        except Exception as e:
            print(f"[Monday] fetch_deals failed: {e}. Falling back to mock.")
            return await MondayMockClient().fetch_deals()

    async def fetch_work_orders(self) -> pd.DataFrame:
        settings = get_settings()
        try:
            df = await self._fetch_board_data(settings.WORK_ORDERS_BOARD_ID)
            # The item name IS the Deal name masked in monday.com
            if "Name" in df.columns and "Deal name masked" not in df.columns:
                df["Deal name masked"] = df["Name"]
            return df
        except Exception as e:
            print(f"[Monday] fetch_work_orders failed: {e}. Falling back to mock.")
            return await MondayMockClient().fetch_work_orders()


def get_monday_service() -> MondayServiceBase:
    settings = get_settings()
    if settings.USE_MOCK_MONDAY:
        return MondayMockClient()
    return MondayGraphQLClient()
