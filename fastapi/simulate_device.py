import asyncio
import httpx
import uuid
from datetime import datetime

BACKEND_URL = "http://localhost:8000"

async def simulate_device():
    print("🚀 SIPARTA IoT Simulator")
    
    device_id = input("Masukkan UUID iot_devices dari Supabase (atau tekan enter untuk menggunakan ID dummy): ")
    if not device_id:
        device_id = str(uuid.uuid4())
        print(f"⚠️ Menggunakan UUID acak: {device_id}. Backend mungkin akan menolak (404) jika ID ini tidak ada di tabel iot_devices.")
        
    print("\nSimulasi dimulai... (Tekan Ctrl+C untuk berhenti)")
    
    async with httpx.AsyncClient() as client:
        while True:
            try:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Mengirim heartbeat untuk {device_id}...")
                resp = await client.post(f"{BACKEND_URL}/api/v1/devices/heartbeat", json={"device_id": device_id})
                
                if resp.status_code == 200:
                    print("✅ Heartbeat berhasil diterima backend.")
                else:
                    print(f"❌ Gagal: {resp.status_code} - {resp.text}")
                    if resp.status_code == 404:
                        print("💡 TIPS: Anda harus membuat 1 record di tabel 'iot_devices' Supabase terlebih dahulu, dan gunakan ID-nya.")
                        break
                        
            except Exception as e:
                print(f"❌ Error koneksi ke backend: {e}")
                
            print("⏳ Menunggu 30 detik sebelum heartbeat berikutnya...\n")
            await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(simulate_device())
