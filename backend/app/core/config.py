import os

DEFAULT_CORS_ORIGINS = "http://localhost:5173"


def get_cors_origins() -> list[str]:
    """CORS_ORIGINS 환경 변수(쉼표 구분)에서 허용할 프론트 주소 목록을 읽는다. (API-000)"""
    raw = os.getenv("CORS_ORIGINS", DEFAULT_CORS_ORIGINS)
    return [origin.strip() for origin in raw.split(",") if origin.strip()]
