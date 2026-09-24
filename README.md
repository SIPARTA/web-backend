# SIPARTA Backend (FastAPI + AI + Blockchain Relay)

Backend SIPARTA dibangun menggunakan **FastAPI** (Python). Backend ini merupakan jantung pengolah data (Central Controller) yang menghubungkan perangkat IoT (*Edge*), Google Gemini AI, Database Relasional (Supabase), dan Blockchain Polygon Amoy.

## 1. Project Overview

Setiap kali terjadi lonjakan deteksi gas di perangkat *Edge*, Raspberry Pi mengirimkan data sensor dan bukti gambar ke backend ini. Backend akan:
1. Meminta analisis ke Google Gemini AI (Mitigation text).
2. Meminta layer Blockchain mencetak rekaman *immutable* di Web3 (menggunakan integrasi native Python `web3.py`).
3. Menyimpan hasil penggabungan akhir ke database Supabase untuk dibaca oleh Frontend.

## 2. Architecture Overview

- **Framework**: FastAPI (Python 3.10+)
- **Database**: Supabase SDK Python
- **AI Integration**: SDK `google-generativeai` (Gemini 2.5 Flash)
- **Web3 Integration**: Menggunakan implementasi *native Python* `web3.py` di dalam modul `services/blockchain/polygon_client.py` (tanpa bergantung pada Node.js atau *subprocess* eksternal).

## 3. Prerequisites

- **Python 3.10** atau lebih baru.
- Mendapatkan kredensial **Supabase** (URL & Service Role Key).
- Kunci API **Google Gemini AI**.
- Kunci Privat Dompet (Wallet Private Key) dengan saldo MATIC di testnet Polygon Amoy.

*(Node.js tidak lagi dibutuhkan untuk menjalankan Backend).*

## 4. Environment Configuration

Salin contoh environment variable:
```bash
cp .env.example .env
```

Isi variabel `.env` berikut (Jangan *commit* file ini!):
- `SUPABASE_URL` = URL proyek Supabase.
- `SUPABASE_SERVICE_ROLE_KEY` = Service role key (Untuk kemampuan admin write tanpa token pengguna).
- `GEMINI_API_KEY` = Kunci API dari Google AI Studio.
- `DEVICE_API_KEY` = Kunci keamanan statis (misal: `siparta_edge_2026`) untuk melindungi API ini dari *spam request* publik. (Harus sama persis dengan `.env` di perangkat RPi).
- `POLYGON_AMOY_PRIVATE_KEY` = Kunci privat dompet *Relayer* Anda.
- `SIPARTA_AUDIT_CONTRACT` = Alamat Smart Contract yang sudah dideploy.
- `PINATA_JWT` = Token JWT dari layanan Pinata IPFS (jika mengunggah metadata ke desentralisasi storage).

## 5. Installation & Setup

1. Buka terminal dan masuk ke direktori `web_backend`.
2. Buat Python Virtual Environment (opsional namun disarankan):
   ```bash
   python -m venv venv
   source venv/bin/activate  # MacOS/Linux
   # venv\Scripts\activate   # Windows
   ```
3. Install package Python:
   ```bash
   pip install -r requirements.txt
   ```

## 6. Running the Application

Jalankan FastAPI di mode development (*hot-reload*):
```bash
uvicorn fastapi.main:app --reload
```
- Server akan berjalan di `http://localhost:8000`.
- Buka `http://localhost:8000/docs` untuk melihat dokumentasi interaktif Swagger API.

## 7. Integration Workflow

**Alur `POST /api/v1/incidents/report`**:
1. Request JSON masuk dari perangkat IoT RPi.
2. Validasi `X-API-Key` dengan `DEVICE_API_KEY`.
3. Validasi status harus bernilai (AMAN / WASPADA / BAHAYA) untuk menghindari *Prompt Injection*.
4. `gemini_service.py` menggabungkan parameter tegangan sensor untuk diproses oleh Gemini AI. Jika terjadi kegagalan jaringan API Google, sistem otomatis memberikan *fallback message* deterministik untuk evakuasi darurat.
5. Memanggil antarmuka internal `PolygonAmoyClient` untuk melakukan pencatatan di Blockchain Polygon.
6. Menyimpan hasil lengkap, termasuk URL IPFS (dari blockchain) dan Transaction Hash, secara sinkron ke Supabase.

## 8. Troubleshooting

- **Symptom**: Gagal menyimpan ke Blockchain Polygon / *Anchoring Timeout*.
  - **Penyebab**: Koneksi ke node RPC gagal atau saldo MATIC pada dompet *Relayer* (`POLYGON_AMOY_PRIVATE_KEY`) tidak cukup.
  - **Solusi**: Pastikan RPC yang terkonfigurasi hidup (mis. `polygon-amoy.drpc.org`) dan isi ulang saldo MATIC testnet melalui Faucet Polygon.
- **Symptom**: `403 Forbidden` atau `Unauthorized`.
  - **Penyebab**: RPi Edge Device tidak mengirimkan header HTTP `X-API-Key` yang sesuai dengan `DEVICE_API_KEY` milik backend.
  - **Solusi**: Periksa kesesuaian `.env` di backend dan `.env` di RPi (`ai_models`).

## 9. Deployment (Render Native Python)

Backend ini dikonfigurasi untuk berjalan secara otomatis dan native di environment **Python 3** pada Render.

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `cd fastapi && uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**:
  Semua kredensial rahasia (Supabase, Gemini, Blockchain) harus ditambahkan secara manual di halaman Settings environment Render. Render akan secara dinamis menyuntikkan variable `PORT` saat runtime.
