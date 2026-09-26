from core.config import settings
from supabase import create_client

db = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
res = db.table("iot_devices").select("*").execute()
print(res.data)
