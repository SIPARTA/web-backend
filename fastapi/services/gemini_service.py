import os
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

# Load .env dari root web-backend (bukan CWD)
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_env_path)

# Setup API Key Google Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))

def analyze_incident_with_gemini(sensor_data: dict, image_path: str):
    """
    Meneruskan foto dari RPi dan data telemetri ke Google Gemini.
    Tujuannya untuk memberikan rekomendasi evakuasi darurat (Mitigasi).
    """
    print("[GEMINI] Meminta analisis Computer Vision dari Google...")
    try:
        # Menggunakan Gemini 1.5 Flash yang sangat cepat & ideal untuk analisis visi
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Upload file gambar barang bukti
        sample_file = genai.upload_file(path=image_path, display_name="SIPARTA_Incident_Visual")
        
        prompt = f"""
        [SISTEM DARURAT SIPARTA]
        Status Bahaya: {sensor_data['status']}
        Data Sensor Gas: {sensor_data['sensors']}
        Waktu Kejadian: {sensor_data['timestamp']}
        
        Tugas Anda sebagai AI Keselamatan:
        1. Analisis gambar terlampir (foto lokasi kejadian). Apakah ada asap tebal, api, kebocoran, atau korban?
        2. Korelasikan dengan tegangan gas (Data di atas).
        3. Berikan 3 poin singkat rekomendasi tindakan evakuasi atau penanganan medis segera!
        """
        
        response = model.generate_content([sample_file, prompt])
        return response.text
        
    except Exception as e:
        print(f"[GEMINI] Gagal memanggil API: {e}")
        return "Gagal mendapatkan analisis AI. Terapkan protokol evakuasi standar."
