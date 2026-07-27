import asyncio, httpx

API_KEY = 'eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjY4NjY1NjYzNCwiYWFpIjoxMSwidWlkIjoxMTE1MDk0OTIsImlhZCI6IjIwMjYtMDctMjdUMDU6NTg6MjguMDAwWiIsInBlciI6Im1lOndyaXRlIiwiYWN0aWQiOjM2MjI0NTA0LCJyZ24iOiJhcHNlMiJ9.MB8ndo3vEPG0Jz-KnvgyLijatCIuWOB25XoLd-ZyppU'
DEALS_BOARD = '5030219755'
WO_BOARD = '5030220085'

# Separate queries - columns metadata + items without title field
COLS_QUERY = """
query ($board: ID!) {
    boards(ids: [$board]) {
        name
        columns { id title type }
    }
}
"""

ITEMS_QUERY = """
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

async def inspect_board(board_id, label):
    async with httpx.AsyncClient(timeout=30) as client:
        headers = {
            'Authorization': API_KEY,
            'API-Version': '2023-10',
            'Content-Type': 'application/json'
        }
        # Step 1: get column id->title map
        r = await client.post('https://api.monday.com/v2',
            json={'query': COLS_QUERY, 'variables': {'board': board_id}},
            headers=headers)
        data = r.json()
        if 'errors' in data:
            print(f'{label} COLUMN ERRORS:', data['errors'])
            return
        board = data['data']['boards'][0]
        col_map = {c['id']: c['title'] for c in board['columns']}
        print(f'=== {label} === Board: {board["name"]}')
        print(f'Columns ({len(col_map)}):')
        for cid, title in col_map.items():
            print(f'  {cid} -> {title}')

        # Step 2: get first page of items
        r2 = await client.post('https://api.monday.com/v2',
            json={'query': ITEMS_QUERY, 'variables': {'board': board_id}},
            headers=headers)
        data2 = r2.json()
        if 'errors' in data2:
            print(f'{label} ITEM ERRORS:', data2['errors'])
            return
        items = data2['data']['boards'][0]['items_page']['items']
        cursor = data2['data']['boards'][0]['items_page']['cursor']
        print(f'\nSample items ({len(items)} on first page, cursor={bool(cursor)}):')
        for item in items[:3]:
            row = {'name': item['name']}
            for cv in item['column_values']:
                title = col_map.get(cv['id'], cv['id'])
                if cv['text']:
                    row[title] = cv['text']
            print(f'  {row}')
        print()

async def main():
    await inspect_board(DEALS_BOARD, 'DEALS')
    await inspect_board(WO_BOARD, 'WORK ORDERS')

asyncio.run(main())
