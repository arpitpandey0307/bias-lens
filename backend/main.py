from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from routers import upload, schema, analyze, export, samples
from error_handlers import (
    BiasLensException,
    biaslens_exception_handler,
    generic_exception_handler
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("BiasLens API starting up...")
    yield
    # Shutdown
    print("BiasLens API shutting down...")

app = FastAPI(
    title="BiasLens API",
    description="Fairness auditing API for AI decision systems",
    version="1.0.0",
    lifespan=lifespan
)

# Register exception handlers
app.add_exception_handler(BiasLensException, biaslens_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router)
app.include_router(schema.router)
app.include_router(analyze.router)
app.include_router(export.router)
app.include_router(samples.router)

@app.get("/")
async def root():
    return {
        "message": "BiasLens API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
