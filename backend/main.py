from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import HTTPException
import logging
import os
from dotenv import load_dotenv

# 导入路由
from app.api.sessions import router as sessions_router
from app.api.users import router as users_router

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用实例
app = FastAPI(
    title="Network Session Analysis API",
    description="网络会话分析系统后端API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://10.33.10.9:3000",
        "http://10.33.10.9:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "message": "Network Session Analysis API is running"
    }

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Network Session Analysis API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# 注册路由
app.include_router(sessions_router, prefix="/api", tags=["sessions"])
app.include_router(users_router, prefix="/api", tags=["users"])

# 启动事件
@app.on_event("startup")
async def startup_event():
    logger.info("Network Session Analysis API starting up...")
    logger.info(f"ClickHouse Host: {os.getenv('CLICKHOUSE_HOST', 'localhost')}")
    logger.info(f"API Server Port: {os.getenv('PORT', '8000')}")

@app.on_event("shutdown") 
async def shutdown_event():
    logger.info("Network Session Analysis API shutting down...")

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )