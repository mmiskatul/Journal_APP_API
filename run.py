from dotenv import load_dotenv
import uvicorn

from app.core.validation import validate_settings

load_dotenv()
validate_settings()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
