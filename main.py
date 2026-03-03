from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.database import init_db, close_db
from app.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("🚀 Starting up...")
    await init_db()
    print("✅ Database initialized")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")
    await close_db()
    print("✅ Database connection closed")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    API для системы перевозки багажей АО «НК «Қазақстан темір жолы»
    
    ## Функционал
    
    * **Авторизация** - регистрация, вход, JWT токены
    * **Документы** - создание, поиск, управление перевозочными документами
    * **Формы** - ЛУ-63, ЛУ-59, ГУ-26
    
    ## Авторизация
    
    Для доступа к защищенным эндпоинтам необходимо передать JWT токен в заголовке:
    ```
    Authorization: Bearer <token>
    ```
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # Изменено с CORS_ORIGINS на cors_origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Ошибка валидации",
            "errors": errors,
        },
    )


# Include routers
app.include_router(api_router)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Проверка работоспособности API."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Корневой эндпоинт."""
    return {
        "message": "KTZh API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
