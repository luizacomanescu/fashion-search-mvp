# scripts/test_supabase.py
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)

result = supabase.table("products").select("*").limit(1).execute()
print("Connected successfully!")
print(result)