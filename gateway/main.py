import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from config import settings
from database import init_db, close_db
from routes import identity, credentials, verification, transaction, grants, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"Starting Identity & Asset Tokenization Gateway")
    print(f"Solana RPC: {settings.solana_rpc_url}")
    print(f"API Setu Environment: {settings.apisetu_env}")

    # Initialize database with retry logic for Render
    try:
        await init_db()  # Uses default 15 retries, 2s base delay
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization failed: {e}")
        raise

    yield

    # Shutdown
    print("Shutting down gateway")
    await close_db()
    print("Database connection closed")


app = FastAPI(
    title="Identity & Asset Tokenization Gateway",
    description="Self-sovereign identity and credential tokenization on Solana",
    version="2.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.sso_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Routes
app.include_router(identity.router, prefix=settings.api_prefix)
app.include_router(credentials.router, prefix=settings.api_prefix)
app.include_router(verification.router, prefix=settings.api_prefix)
app.include_router(transaction.router, prefix=settings.api_prefix)
app.include_router(grants.router, prefix=settings.api_prefix)
app.include_router(auth.router, prefix=settings.api_prefix)


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.1.0",
        "solana_rpc": settings.solana_rpc_url,
        "apisetu_env": settings.apisetu_env,
    }


@app.get("/")
async def root():
    return {
        "name": "Identity & Asset Tokenization Gateway",
        "version": "2.1.0",
        "docs": "/docs",
    }
