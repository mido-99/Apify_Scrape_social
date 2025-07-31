import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    APIFY_API = os.getenv("APIFY_API")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

settings = Settings() 