"""
SIPARTA Backend — Web3 Service Layer
======================================
Jembatan Python → TypeScript Relay (relay_runner.ts).

Kenapa pakai subprocess ke TS alih-alih web3.py langsung?
  - relay.ts sudah memiliki logika EIP-1559, retry, dan ABI management yang matang.
  - Menghindari duplikasi logic blockchain di dua bahasa.
  - Relay TS bisa di-scale independen sebagai microservice.

Catatan Dual-Mode:
  - Jika SIPARTA_AUDIT_CONTRACT diset → relay.ts pakai PRIMARY mode (SipartaAudit).
  - Jika hanya GAS_DETECTION_CONTRACT diset → relay.ts pakai LEGACY mode (GasDetectionStorage).
  - Mode dipilih otomatis di relay.ts berdasarkan env var.
"""

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger("siparta.web3_service")

# Path ke relay_runner.ts (relatif dari web-backend)
_RELAY_DIR = Path(__file__).resolve().parent.parent.parent.parent / "blockchain_services"
_RELAY_SCRIPT = _RELAY_DIR / "src" / "relay_runner.ts"


import asyncio

async def _run_relay(action: str, **kwargs) -> Optional[dict]:
    """
    Helper: menjalankan relay_runner.ts via subprocess dan mem-parse output JSON-nya secara asynchronous.
    """
    if not _RELAY_SCRIPT.exists():
        logger.error(f"[WEB3] relay_runner.ts tidak ditemukan: {_RELAY_SCRIPT}")
        return None

    args = ["npx", "tsx", str(_RELAY_SCRIPT), "--action", action]
    if "payload" in kwargs:
        args += ["--payload", json.dumps(kwargs["payload"])]
    if "uuid" in kwargs:
        args += ["--uuid", kwargs["uuid"]]

    logger.info(f"[WEB3] Memanggil relay: action={action}")

    try:
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(_RELAY_DIR),
            env={**os.environ},
        )
        
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120)
        stdout_str = stdout.decode()
        stderr_str = stderr.decode()

        stdout_lines = [line.strip() for line in stdout_str.splitlines() if line.strip()]
        if not stdout_lines:
            logger.error(f"[WEB3] Relay output kosong.\nSTDERR: {stderr_str[:500]}")
            return None

        last_line = stdout_lines[-1]
        parsed = json.loads(last_line)

        if process.returncode != 0:
            logger.warning(
                f"[WEB3] Relay exited {process.returncode}. "
                f"Parsed: {parsed}. STDERR: {stderr_str[:300]}"
            )
        else:
            logger.info(f"[WEB3] Relay sukses: {parsed}")

        return parsed

    except asyncio.TimeoutError:
        logger.error("[WEB3] Relay timeout (120s). Blockchain mungkin padat.")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"[WEB3] Gagal parse JSON dari relay: {e}")
        return None
    except Exception as e:
        logger.error(f"[WEB3] Relay error: {e}")
        return None


async def log_incident_to_blockchain(payload: dict) -> dict:
    """
    Mencatat insiden ke Polygon Amoy via relay.ts.
    """
    result = await _run_relay("anchor", payload=payload)
    if result is None:
        return {"txHash": None, "blockNumber": 0, "mode": "error"}
    return result


async def verify_incident_on_chain(incident_uuid: str) -> bool:
    """
    Verifikasi apakah insiden sudah tercatat di SipartaAudit contract.
    """
    result = await _run_relay("verify", uuid=incident_uuid)
    if result is None:
        return False
    return bool(result.get("verified", False))
