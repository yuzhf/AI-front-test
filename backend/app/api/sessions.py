from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.models.schemas import SessionResponse, QueryParams, StatsResponse
from app.services.clickhouse_service import get_clickhouse_service
from app.services.auth_service import get_current_user

router = APIRouter()

@router.get("/sessions", response_model=SessionResponse)
async def get_sessions(
    start_time: Optional[str] = Query(None, description="开始时间 (YYYY-MM-DD HH:MM:SS)"),
    end_time: Optional[str] = Query(None, description="结束时间 (YYYY-MM-DD HH:MM:SS)"),
    src_ip: Optional[str] = Query(None, description="源IP地址"),
    dst_ip: Optional[str] = Query(None, description="目标IP地址"),
    protocol: Optional[str] = Query(None, description="协议类型"),
    app_name: Optional[str] = Query(None, description="应用名称"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    current_user: dict = Depends(get_current_user)
):
    """获取会话数据列表"""
    try:
        offset = (page - 1) * size
        result = get_clickhouse_service().get_session_data(
            start_time=start_time,
            end_time=end_time,
            src_ip=src_ip,
            dst_ip=dst_ip,
            protocol=protocol,
            app_name=app_name,
            limit=size,
            offset=offset
        )
        
        return SessionResponse(
            data=result["data"],
            total=result["total"],
            page=page,
            size=size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取会话数据失败: {str(e)}")

@router.get("/sessions/stats")
async def get_session_stats(current_user: dict = Depends(get_current_user)):
    """获取会话统计信息"""
    try:
        stats = get_clickhouse_service().get_session_stats()

        # 返回原始数据，让前端处理格式化
        return {
            "total_sessions": stats["total_sessions"],
            "total_packets": stats["total_packets"],
            "total_traffic": stats["total_traffic"],  # 总字节数
            "unique_ips": stats["unique_ips"],
            "last_activity": stats["last_activity"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

@router.get("/sessions/top-ips")
async def get_top_ips(
    limit: int = Query(10, ge=1, le=50, description="返回数量限制"),
    current_user: dict = Depends(get_current_user)
):
    """获取热门IP统计"""
    try:
        top_ips = get_clickhouse_service().get_top_ips(limit=limit)

        # 返回原始数据，前端处理格式化
        formatted_ips = []
        for ip_data in top_ips:
            formatted_ips.append({
                "ip": ip_data["ip"],
                "session_count": ip_data["sessions"],  # 会话数
                "total_bytes": ip_data["traffic_bytes"]  # 字节数
            })

        return formatted_ips

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取热门IP失败: {str(e)}")

@router.get("/sessions/protocols")
async def get_protocol_stats(current_user: dict = Depends(get_current_user)):
    """获取协议统计信息"""
    try:
        protocols = get_clickhouse_service().get_protocol_stats()
        return protocols
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取协议统计失败: {str(e)}")

@router.get("/sessions/time-range")
async def get_time_range(current_user: dict = Depends(get_current_user)):
    """获取数据的时间范围"""
    try:
        time_range = get_clickhouse_service().get_time_range()
        return time_range
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取时间范围失败: {str(e)}")

@router.get("/sessions/export")
async def export_sessions(
    format: str = Query("csv", description="导出格式: csv, json, xlsx"),
    start_time: Optional[str] = Query(None),
    end_time: Optional[str] = Query(None),
    src_ip: Optional[str] = Query(None),
    dst_ip: Optional[str] = Query(None),
    protocol: Optional[str] = Query(None),
    app_name: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """导出会话数据"""
    try:
        # 获取所有符合条件的数据
        result = get_clickhouse_service().get_session_data(
            start_time=start_time,
            end_time=end_time,
            src_ip=src_ip,
            dst_ip=dst_ip,
            protocol=protocol,
            app_name=app_name,
            limit=10000,  # 限制最多导出10000条
            offset=0
        )
        
        if format.lower() == "json":
            from fastapi.responses import JSONResponse
            return JSONResponse(content=result["data"])
        
        # 对于CSV和Excel格式，这里返回数据，实际项目中可以生成文件
        return {
            "message": f"导出{format}格式数据",
            "total_records": len(result["data"]),
            "data": result["data"][:10]  # 只返回前10条作为预览
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出数据失败: {str(e)}")