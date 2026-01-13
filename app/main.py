from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.routes import router
from app.core.config import settings
from app.core.limiter import limiter 

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="AI Backend for Halal Food Analysis with OCR & Fuzzy Logic"
)

# 1. PASANG CORS (WAJIB BUAT REACT)
origins = [
    "http://localhost:5173", 
    "http://127.0.0.1:5173",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Boleh GET, POST, dll
    allow_headers=["*"],  # Boleh bawa header apa aja (termasuk x-api-key)
)

# 2. PASANG RATE LIMITER (SATPAM)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Register Router
app.include_router(router, prefix=settings.API_V1_STR)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "TrustBite AI is Ready 🚀"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)