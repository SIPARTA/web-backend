import os
import asyncio
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Missing SUPABASE credentials")
    exit(1)

supabase: Client = create_client(url, key)

try:
    response = supabase.table("iot_devices").select("*").limit(1).execute()
    print("Table iot_devices exists:", response)
except Exception as e:
    print("Error querying iot_devices:", e)
