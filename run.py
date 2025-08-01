import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)