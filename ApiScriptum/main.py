from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health
from app.config import settings

app = FastAPI(
    title="Scriptum",
    description="API para la app Scriptum",
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

@app.post("/vigenere/cifrar/texto")
async def vigenere_cifrar(text: str, key: str):
    return {
        "message": "Cifrado Vigenère",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/vigenere/decifrar/texto")
async def vigenere_decifrar():
    return {
        "message": "Decifrado Vigenère",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.post("/vigenere/cifrar/file")
async def vigenere_cifrar_file(file: UploadFile, key: str):
    return {
        "message": "Cifrado Vigenère de archivo",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/vigenere/decifrar/file")
async def vigenere_decifrar_file():
    return {
        "message": "Decifrado Vigenère de archivo",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.post("/aes/cifrar/texto")
async def aes_cifrar(text: str, key: str, longitud: int):
    return {
        "message": "Cifrado AES",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/aes/decifrar/texto")
async def aes_decifrar():
    return {
        "message": "Decifrado AES",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.post("/aes/cifrar/file")
async def aes_cifrar_file(file: UploadFile, key: str, longitud: int):
    return {
        "message": "Cifrado AES de archivo",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/aes/decifrar/file")
async def aes_decifrar_file():
    return {
        "message": "Decifrado AES de archivo",
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
