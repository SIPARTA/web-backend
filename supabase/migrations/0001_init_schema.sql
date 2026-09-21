-- ========================================================================================
-- SIPARTA (Sistem Informasi Keselamatan Bahaya Kimia)
-- Supabase PostgreSQL Schema & ERD Setup
-- ========================================================================================

-- Enable UUID extension untuk security (menghindari ID guessing)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- 1. DOMAIN: IDENTITY & ACCESS (USERS)
-- ==========================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wallet_address VARCHAR(42) UNIQUE, -- Address Polygon/EVM (Web3)
    role VARCHAR(20) NOT NULL DEFAULT 'student', -- enum: admin, lab_assistant, student
    nonce VARCHAR(255), -- Security nonce untuk verifikasi SIWE (Sign-In With Ethereum)
    name VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ==========================================
-- 2. DOMAIN: IOT & EDGE AI (DEVICES)
-- ==========================================
CREATE TABLE iot_devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL, -- Contoh: "Raspberry Pi 3 B+ - Lab Biokimia"
    location VARCHAR(255) NOT NULL,
    api_key_hash VARCHAR(255) NOT NULL, -- Auth Token dari RPi (Hashed)
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ==========================================
-- 3. DOMAIN: REAL-TIME TELEMETRY & LOGS
-- ==========================================
-- Tabel ini adalah jantung dari sistem, menampung payload dari main_rpi.py
CREATE TABLE incident_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id UUID NOT NULL REFERENCES iot_devices(id) ON DELETE CASCADE,
    
    incident_type VARCHAR(100) NOT NULL, -- Klasifikasi AI: 'GAS_LEAK', 'TOXIC_MIXTURE', 'SAFE'
    severity VARCHAR(50) NOT NULL,       -- Berdasarkan status: 'AMAN', 'WASPADA', 'BAHAYA'
    
    -- Telemetri Sensor Gas (JSONB sangat ideal untuk fleksibilitas IoT di Supabase)
    -- Format: {"mics5524": 3.12, "tgs2600": 2.45, "mq2": 1.20, "mq135": 3.55}
    sensor_data JSONB,                   
    
    image_url TEXT,                      -- Path file gambar bukti (Supabase Storage)
    ai_analysis_text TEXT,               -- Hasil teks instruksi mitigasi dari Google Gemini AI
    
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_anchored BOOLEAN NOT NULL DEFAULT false -- Status flag apakah sudah masuk Blockchain
);
-- Indexing agar dashboard monitoring dan pencarian tanggal berjalan super cepat
CREATE INDEX idx_incident_events_device_timestamp ON incident_events(device_id, timestamp);

-- ==========================================
-- 4. DOMAIN: WEB3 BLOCKCHAIN TRACKER
-- ==========================================
CREATE TABLE transactions_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tx_hash VARCHAR(66) UNIQUE, -- Hash transaksi Polygon Amoy
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING', -- enum: 'PENDING', 'SUCCESS', 'FAILED'
    
    -- Polymorphic Relation untuk fleksibilitas
    entity_type VARCHAR(50) NOT NULL, -- 'INCIDENT' (untuk log) atau 'CERTIFICATE' (Edukasi K3)
    entity_id UUID NOT NULL,          -- Merujuk ke incident_events.id
    
    retry_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ==========================================
-- 5. DOMAIN: IMMUTABLE AUDIT TRAIL
-- ==========================================
-- Tabel khusus untuk membuktikan validitas data (Anchor ke Web3)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id UUID NOT NULL UNIQUE REFERENCES incident_events(id) ON DELETE CASCADE,
    tx_id UUID NOT NULL REFERENCES transactions_logs(id) ON DELETE CASCADE,
    
    ipfs_cid VARCHAR(255), -- ID IPFS tempat metadata disimpan
    block_number BIGINT,   -- Nomor blok Polygon saat transaksi tervalidasi
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ==========================================
-- REALTIME ENABLEMENT (WAJIB UNTUK NEXT.JS)
-- ==========================================
-- Agar websocket dashboard Next.js dapat mendengarkan insert pada tabel ini:
alter publication supabase_realtime add table incident_events;
alter publication supabase_realtime add table transactions_logs;
alter publication supabase_realtime add table audit_logs;
