import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from app.config import get_settings
from app.database import init_db
from app.redis_client import redis_client
from app.middleware import log_requests_middleware, catch_exceptions_middleware, rate_limit_exceeded_handler, limiter
from app.routers import auth, books, borrow

settings = get_settings()

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

app = FastAPI(
    title="Library Management System",
    description="A production-ready library management system with authentication, book management, and borrowing system.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(429, rate_limit_exceeded_handler)

# Custom middlewares
app.middleware("http")(log_requests_middleware)
app.middleware("http")(catch_exceptions_middleware)

# Include routers
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(borrow.router)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")
    init_db()
    await redis_client.connect()
    logger.info("Connected to Redis")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")
    await redis_client.close()

@app.get("/")
async def root():
    return {"message": "Library Management System API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
