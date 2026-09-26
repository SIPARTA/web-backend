-- Migration 0002: Perbaikan ERD untuk Relasi User & IoT Status

-- 1. Tambahkan relasi user_id ke iot_devices untuk menunjukkan kepemilikan perangkat
ALTER TABLE iot_devices ADD COLUMN user_id UUID REFERENCES users(id) ON DELETE SET NULL;

-- 2. Tambahkan kolom last_seen ke iot_devices untuk fitur heartbeat/status online
ALTER TABLE iot_devices ADD COLUMN last_seen TIMESTAMPTZ;

-- 3. Pastikan wallet_address unik agar bisa di-upsert saat login MetaMask
-- (Sudah ada di 0001_init_schema.sql, tetapi jika live DB menggunakan bigint dan belum unik, ini men-enforce-nya)
-- ALTER TABLE users ADD CONSTRAINT users_wallet_address_key UNIQUE (wallet_address);
