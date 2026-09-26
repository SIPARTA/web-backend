-- Migration 0004: Memperbaiki tabel transaction_logs
-- Tambahkan kolom created_at yang terlewat

ALTER TABLE transaction_logs 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
