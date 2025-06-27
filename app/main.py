from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.api.routes import analysis, refactor, github
from core.ml.models.classifier import CodeSmellClassifier
from utils.logger import setup_logger

# Global model instances
models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load ML models
    logger = setup_logger(__name__)
    logger.info("Loading ML models...")
    
    models["classifier"] = CodeSmellClassifier()
    models["classifier"].load_model()
    
    logger.info("Models loaded successfully!")
    yield
    # Shutdown: cleanup if needed
    models.clear()

app = FastAPI(
    title="AI Code Refactor Assistant",
    description="AI-powered code analysis and refactoring suggestions",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(refactor.router, prefix="/api/v1/refactor", tags=["refactor"])
app.include_router(github.router, prefix="/api/v1/github", tags=["github"])

# Static files (for frontend)
app.mount("/static", StaticFiles(directory="frontend/build"), name="static")

@app.get("/")
async def root():
    return {"message": "AI Code Refactor Assistant API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "models_loaded": len(models)}