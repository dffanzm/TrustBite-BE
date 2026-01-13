from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from app.services.ocr_engine import ai_engine
from app.models.schemas import AnalysisResult
from app.core.security import get_api_key
from app.core.limiter import limiter 

router = APIRouter()

@router.post("/analyze", response_model=AnalysisResult)
@limiter.limit("10/minute") # SECURITY: Max 10 request per menit per IP
async def analyze_food(
    request: Request, # <--- WAJIB ADA buat SlowAPI
    file: UploadFile = File(...),
    api_key: str = Depends(get_api_key) # SECURITY CHECK
):
    # 1. Validasi Tipe File
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, detail="File harus berupa gambar (jpg/png)")
    
    # 2. Baca File
    try:
        contents = await file.read()
    except Exception:
        raise HTTPException(500, detail="Gagal membaca file upload")

    # 3. PROSES UTAMA (OCR + Analisis)
    # Kita panggil satu fungsi 'analyze_image' yang sudah mengurus semuanya:
    # - Preprocessing gambar
    # - OCR (Baca teks)
    # - Cleaning teks
    # - Pencocokan Halal/Haram
    try:
        result = ai_engine.analyze_image(contents)
        return result
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        # Return error 500 kalau ada crash di engine
        raise HTTPException(status_code=500, detail=f"AI Engine Error: {str(e)}")