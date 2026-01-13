import secrets
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.core.config import settings

# auto_error=False biar kita bisa handle error message sendiri
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    # 1. Cek kalau user lupa bawa kunci (Header kosong)
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key Header"
        )
        
    # 2. Cek kunci dengan 'secrets.compare_digest' (Lebih aman dari == biasa)
    # Ini mencegah Timing Attack
    is_valid = secrets.compare_digest(api_key_header, settings.API_SECRET_KEY)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key credentials"
        )
        
    # 3. Kalau lolos, balikin kuncinya
    return api_key_header