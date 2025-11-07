from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health
from app.config import settings

app = FastAPI(
    title="Scriptum API",
    description="API para el proyecto Scriptum",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(health.router, tags=["Health"])

@app.get("/")
async def root():
    return {
        "message": "Bienvenido a Scriptum API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
