export interface Token {
  access_token: string;
  token_type: string;
}

export interface UserInfo {
  username: string;
  role: string;
}

export interface UserResponse {
  id: number;
  username: string;
  full_name: string | null;
  email: string | null;
  role: string;
  is_active: boolean;
  created_at: string | null;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  history: ChatMessage[];
}

export interface ChatResponse {
  reply: string;
  data: Record<string, unknown> | null;
  data_quality_notes: string[];
  tool_used: string | null;
}

export interface DealSummary {
  total_deals: number;
  won: number;
  dead: number;
  open: number;
  on_hold: number;
  win_rate: number;
  total_pipeline_value: number;
  avg_deal_value: number;
}

export interface PipelineStage {
  stage: string;
  count: number;
  value: number;
}

export interface SectorBreakdown {
  sector: string;
  count: number;
  value: number;
}

export interface WorkOrderSummary {
  total_orders: number;
  completed: number;
  ongoing: number;
  not_started: number;
  paused: number;
  total_contract_value: number;
  billed_value: number;
  collected_value: number;
  ar_outstanding: number;
}

export interface DataQualityReport {
  deals_total: number;
  deals_missing_sector: number;
  deals_missing_close_date: number;
  deals_duplicate_headers_removed: number;
  wo_total: number;
  wo_missing_amounts: number;
  wo_excel_errors_fixed: number;
  wo_missing_dates: number;
  cleaning_steps: string[];
}

export interface MonthlyRevenue {
  month: string;
  billed: number;
  collected: number;
}

export interface AnalyticsDashboard {
  deal_summary: DealSummary;
  pipeline_stages: PipelineStage[];
  sector_breakdown_deals: SectorBreakdown[];
  sector_breakdown_wo: SectorBreakdown[];
  work_order_summary: WorkOrderSummary;
  monthly_revenue: MonthlyRevenue[];
  data_quality: DataQualityReport;
}
