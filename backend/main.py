"""
IdentityAI - Main FastAPI Application.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.routers import providers, sources, patents, analysis

app = FastAPI(
    title="IdentityAI",
    description="Ultra-minimalist brand identity protection and impersonation intelligence.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(providers.router)
app.include_router(sources.router)
app.include_router(patents.router)
app.include_router(analysis.router)

# Mount static directory for the single-page glassmorphism frontend
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def serve_index():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "IdentityAI API is running. UI building..."}

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "identity-ai"}
