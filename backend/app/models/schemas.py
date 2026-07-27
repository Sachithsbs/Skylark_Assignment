from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = ""
    email: Optional[str] = ""

class UserInfo(BaseModel):
    username: str
    role: str

class UserResponse(BaseModel):
    id: int
    username: str
    full_name: Optional[str]
    email: Optional[str]
    role: str
    is_active: bool
    created_at: Optional[datetime]

    class Config:
        from_attributes = True

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []

class ChatResponse(BaseModel):
    reply: str
    data: Optional[Dict[str, Any]] = None
    data_quality_notes: List[str] = []
    tool_used: Optional[str] = None

class DealSummary(BaseModel):
    total_deals: int
    won: int
    dead: int
    open: int
    on_hold: int
    win_rate: float
    total_pipeline_value: float
    avg_deal_value: float

class PipelineStage(BaseModel):
    stage: str
    count: int
    value: float

class SectorBreakdown(BaseModel):
    sector: str
    count: int
    value: float

class WorkOrderSummary(BaseModel):
    total_orders: int
    completed: int
    ongoing: int
    not_started: int
    paused: int
    total_contract_value: float
    billed_value: float
    collected_value: float
    ar_outstanding: float

class DataQualityReport(BaseModel):
    deals_total: int
    deals_missing_sector: int
    deals_missing_close_date: int
    deals_duplicate_headers_removed: int
    wo_total: int
    wo_missing_amounts: int
    wo_excel_errors_fixed: int
    wo_missing_dates: int
    cleaning_steps: List[str]

class AnalyticsDashboard(BaseModel):
    deal_summary: DealSummary
    pipeline_stages: List[PipelineStage]
    sector_breakdown_deals: List[SectorBreakdown]
    sector_breakdown_wo: List[SectorBreakdown]
    work_order_summary: WorkOrderSummary
    monthly_revenue: List[Dict[str, Any]]
    data_quality: DataQualityReport
