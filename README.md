# SIPARTA Backend (FastAPI + AI + Blockchain Relay)

Backend SIPARTA dibangun menggunakan **FastAPI** (Python). Backend ini merupakan jantung pengolah data (Central Controller) yang menghubungkan perangkat IoT (*Edge*), Google Gemini AI, Database Relasional (Supabase), dan Blockchain Polygon (via subprocess ke `blockchain_services`).

## 1. Project Overview

Setiap kali terjadi lonjakan deteksi gas di perangkat *Edge*, Raspberry Pi mengirimkan data sensor dan bukti gambar ke backend ini. Backend akan:
1. Meminta analisis ke Google Gemini AI (Mitigation text).
2. Meminta layer Blockchain mencetak rekaman *immutable* di Web3 (menggunakan skrip Node.js).
3. Menyimpan hasil penggabungan akhir ke database Supabase untuk dibaca oleh Frontend.

## 2. Architecture Overview

- **Framework**: FastAPI (Python 3.10+)
- **Database**: Supabase SDK Python
- **AI Integration**: SDK `google-generativeai` (Gemini 2.5 Flash)
- **Web3 Integration**: Melakukan eksekusi asinkron `subprocess.run(["npx", "ts-node", "relay.ts"])` dengan lokasi kerja (CWD) `blockchain_services`.

## 3. Prerequisites

- **Python 3.10** atau lebih baru.
- **Node.js** dan **npm** (wajib ada karena backend akan memanggil subprocess Node).
- Instalasi `npm install` sudah dilakukan di direktori `../blockchain_services`.
- Mendapatkan kredensial **Supabase** (URL & Service Role Key).
- Kunci API **Google Gemini AI**.

## 4. Environment Configuration

Salin contoh environment variable:
```bash
cp .env.example .env
```

Isi variabel `.env` berikut (Jangan *commit* file ini!):
- `SUPABASE_URL` = URL proyek Supabase.
- `SUPABASE_SERVICE_ROLE_KEY` = Service role key (Untuk kemampuan admin write tanpa token pengguna).
- `GEMINI_API_KEY` = Kunci API dari Google AI Studio.
- `DEVICE_API_KEY` = Tentukan sembarang kunci keamanan statis (misal: `siparta_edge_2026`) untuk melindungi API ini dari *spam request* publik. (Harus disamakan dengan `.env` di RPi).

*Catatan: Environment variable lain (seperti `RELAYER_PRIVATE_KEY` atau `PINATA_JWT`) diletakkan di `blockchain_services/.env` namun akan otomatis terbaca jika backend menjalankan subprocess dari sana.*

## 5. Installation & Setup

1. Buka terminal dan masuk ke direktori `web-backend`.
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
3. Validasi status harus bernilai (AMAN / WASPADA / BAHAYA) untuk perlindungan *Prompt Injection*.
4. `gemini_service.py` menggabungkan parameter tegangan sensor untuk diproses oleh Gemini AI. Jika terjadi kegagalan jaringan API Google, sistem otomatis memberikan *fallback message* deterministik untuk evakuasi darurat.
5. Memanggil skrip Typescript di luar proses Python untuk Web3.
6. Menyimpan hasil lengkap, termasuk URL IPFS (dari blockchain) dan Transaction Hash, ke Supabase.

## 8. Troubleshooting

- **Symptom**: Transaksi blockchain *Timeout* atau *Error Parsing JSON*.
  - **Penyebab**: Direktori `blockchain_services` belum dilakukan `npm install`, atau `relay.ts` mengalami *crash* akibat kurang saldo Matic di *Relayer Wallet*.
  - **Solusi**: Cek terminal log. Pastikan Anda bisa menjalankan perintah `npx ts-node src/relay.ts` secara manual di dalam direktori `blockchain_services`.
- **Symptom**: `403 Forbidden` atau `Unauthorized`.
  - **Penyebab**: RPi Edge Device tidak mengirimkan header HTTP `X-API-Key` yang sesuai dengan `DEVICE_API_KEY` milik backend.
  - **Solusi**: Periksa `.env` di backend dan `.env` di RPi (`ai_models`).

## 9. Deployment (Render Native Python)

Backend ini dikonfigurasi untuk berjalan langsung secara native di environment **Python 3** pada Render, tanpa menggunakan Docker.

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn fastapi.main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**:
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_ROLE_KEY`
  - `GEMINI_API_KEY`
  - `DEVICE_API_KEY`

Render akan secara dinamis menyuntikkan environment variable `PORT`, dan `uvicorn` akan menggunakannya untuk *binding* aplikasi ke port tersebut dengan host `0.0.0.0`.
