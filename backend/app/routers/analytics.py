from fastapi import APIRouter, Depends
from app.models.schemas import AnalyticsDashboard, PipelineStage, SectorBreakdown, WorkOrderSummary, DataQualityReport, UserInfo
from app.services.analytics_service import AnalyticsService
from app.services.monday_service import get_monday_service
from app.utils.security import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])
analytics_service = AnalyticsService()

@router.get("/dashboard", response_model=AnalyticsDashboard)
async def get_dashboard(current_user: UserInfo = Depends(get_current_user)):
    monday_svc = get_monday_service()
    return await analytics_service.get_full_dashboard(monday_svc)

@router.get("/pipeline", response_model=list[PipelineStage])
async def get_pipeline(current_user: UserInfo = Depends(get_current_user)):
    monday_svc = get_monday_service()
    deals_df, _ = await analytics_service._get_data(monday_svc)
    return analytics_service.get_pipeline_stages(deals_df)

@router.get("/sectors", response_model=dict)
async def get_sectors(current_user: UserInfo = Depends(get_current_user)):
    monday_svc = get_monday_service()
    deals_df, wo_df = await analytics_service._get_data(monday_svc)
    return {
        "deals": analytics_service.get_sector_breakdown_deals(deals_df),
        "wo": analytics_service.get_sector_breakdown_wo(wo_df)
    }

@router.get("/work-orders", response_model=WorkOrderSummary)
async def get_work_orders(current_user: UserInfo = Depends(get_current_user)):
    monday_svc = get_monday_service()
    _, wo_df = await analytics_service._get_data(monday_svc)
    return analytics_service.get_work_order_summary(wo_df)

@router.get("/data-quality", response_model=DataQualityReport)
async def get_data_quality(current_user: UserInfo = Depends(get_current_user)):
    monday_svc = get_monday_service()
    deals_df, wo_df = await analytics_service._get_data(monday_svc)
    return analytics_service.get_data_quality_report(deals_df, wo_df, analytics_service._deals_cleaning_steps + analytics_service._wo_cleaning_steps)
