-- Migration 0005: Refactor transaction_logs and audit_log
-- Menghapus polimorfisme, membalik relasi agar transaction_logs mereferensikan audit_log.
-- Mengamankan tipe data (block_number int8).

-- 1. Pastikan nama tabel konsisten (jika masih transactions_logs, rename menjadi transaction_logs)
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'transactions_logs') THEN
        ALTER TABLE transactions_logs RENAME TO transaction_logs;
    END IF;
    IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'audit_logs') THEN
        ALTER TABLE audit_logs RENAME TO audit_log;
    END IF;
END $$;

-- 2. Refactor `audit_log`
-- Drop tx_id constraint & column karena sekarang transaction_logs yang akan menunjuk ke audit_log
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'audit_log' AND column_name = 'tx_id') THEN
        ALTER TABLE audit_log DROP COLUMN tx_id CASCADE;
    END IF;
END $$;

-- Pastikan block_number bertipe BIGINT (int8)
ALTER TABLE audit_log ALTER COLUMN block_number TYPE BIGINT;
ALTER TABLE audit_log ADD COLUMN IF NOT EXISTS ipfs_cid VARCHAR(255);

-- 3. Refactor `transaction_logs`
-- Hapus kolom polimorfik yang rentan type-mismatch
ALTER TABLE transaction_logs DROP COLUMN IF EXISTS entity_type CASCADE;
ALTER TABLE transaction_logs DROP COLUMN IF EXISTS entity_id CASCADE;

-- Tambahkan kolom relasi baru ke audit_log
ALTER TABLE transaction_logs ADD COLUMN IF NOT EXISTS audit_log_id UUID REFERENCES audit_log(id) ON DELETE CASCADE;

-- Tambahkan kolom error_message & updated_at
ALTER TABLE transaction_logs ADD COLUMN IF NOT EXISTS error_message TEXT;
ALTER TABLE transaction_logs ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- Ubah retry_count dari int4 ke int2
ALTER TABLE transaction_logs ALTER COLUMN retry_count TYPE SMALLINT;

-- 4. Indeks untuk Optimasi Pencarian
CREATE INDEX IF NOT EXISTS idx_transaction_logs_tx_hash ON transaction_logs(tx_hash);
CREATE INDEX IF NOT EXISTS idx_transaction_logs_audit_log_id ON transaction_logs(audit_log_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_incident_event_id ON audit_log(incident_event_id);
