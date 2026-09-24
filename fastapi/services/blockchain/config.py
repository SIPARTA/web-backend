"""Environment-driven configuration for the Polygon Amoy integration.

Secrets (private key) are ONLY ever read from environment variables —
never defaults, never literals, never logged.  A ``.env`` file at the
project root is parsed (if present) so deployments stay friction-free;
values already present in ``os.environ`` always win.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
ABI_FILE = Path(__file__).resolve().parent / "siparta_audit_abi.json"

DEFAULT_CHAIN_ID = 80002          # Polygon Amoy testnet
DEFAULT_REQUEST_TIMEOUT_S = 15    # per RPC HTTP request
DEFAULT_RECEIPT_TIMEOUT_S = 180   # wait_for_transaction_receipt


def ensure_dotenv(path: Path | None = None) -> bool:
    """Parse ``KEY=VALUE`` lines from *path* into ``os.environ``.

    Existing environment variables are never overridden.  Values are
    deliberately NOT logged (the file holds the private key).
    """
    env_path = path if path is not None else ENV_FILE
    if not env_path.exists():
        return False
    try:
        raw = env_path.read_text(encoding="utf-8")
    except OSError as exc:
        logger.warning("Could not read %s: %s", env_path.name, exc)
        return False
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value
    return True


def load_abi(path: Path | None = None) -> list[dict[str, Any]]:
    """Load the GasDetectionStorage ABI shipped with the project."""
    abi_path = path if path is not None else ABI_FILE
    try:
        with open(abi_path, "r", encoding="utf-8") as fh:
            abi = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Cannot load contract ABI from {abi_path}: {exc}") from exc
    if not isinstance(abi, list):
        raise RuntimeError(f"Contract ABI at {abi_path} is malformed")
    return abi


class BlockchainConfig:
    """Immutable snapshot of blockchain-related settings."""

    def __init__(
        self,
        rpc_url: str,
        private_key: str,
        contract_address: str,
        chain_id: int,
        enabled: bool,
        evidence_base_url: str,
        request_timeout_s: int,
        receipt_timeout_s: int,
        pinata_jwt: str,
    ) -> None:
        self.rpc_url = rpc_url.strip()
        self.private_key = private_key.strip()
        self.contract_address = contract_address.strip()
        self.chain_id = chain_id
        self.enabled = enabled
        self.evidence_base_url = evidence_base_url.strip().rstrip("/")
        self.request_timeout_s = request_timeout_s
        self.receipt_timeout_s = receipt_timeout_s
        self.pinata_jwt = pinata_jwt.strip()

    @classmethod
    def load(cls) -> "BlockchainConfig":
        """Build a config from environment (loading .env first)."""
        ensure_dotenv()

        def _env(key: str, default: str = "") -> str:
            return os.environ.get(key, default)

        chain_id_raw = _env("POLYGON_AMOY_CHAIN_ID", str(DEFAULT_CHAIN_ID))
        try:
            chain_id = int(chain_id_raw)
        except ValueError:
            logger.warning(
                "POLYGON_AMOY_CHAIN_ID=%r is not an integer — using %d",
                chain_id_raw, DEFAULT_CHAIN_ID,
            )
            chain_id = DEFAULT_CHAIN_ID

        enabled_raw = _env("BLOCKCHAIN_ENABLED", "false").strip().lower()
        enabled = enabled_raw in ("1", "true", "yes", "on")

        # Either PINATA_JWT or fallback to trying to use something else, but we just load PINATA_JWT
        return cls(
            rpc_url=_env("POLYGON_AMOY_RPC_URL"),
            private_key=_env("POLYGON_AMOY_PRIVATE_KEY") or _env("RELAYER_PRIVATE_KEY"),
            contract_address=_env("SIPARTA_AUDIT_CONTRACT") or _env("POLYGON_AMOY_CONTRACT_ADDRESS"),
            chain_id=chain_id,
            enabled=enabled,
            evidence_base_url=_env("EVIDENCE_BASE_URL"),
            request_timeout_s=DEFAULT_REQUEST_TIMEOUT_S,
            receipt_timeout_s=DEFAULT_RECEIPT_TIMEOUT_S,
            pinata_jwt=_env("PINATA_JWT"),
        )

    @property
    def has_credentials(self) -> bool:
        """True when every mandatory variable is non-empty."""
        return bool(
            self.rpc_url and self.private_key and self.contract_address
        )

    def safe_summary(self) -> dict[str, Any]:
        """Log-friendly view — secrets are masked out."""
        def _mask(secret: str) -> str:
            return f"<set:{len(secret)} chars>" if secret else "<unset>"

        from urllib.parse import urlparse

        host = urlparse(self.rpc_url).netloc if self.rpc_url else ""
        return {
            "enabled": self.enabled,
            "rpc_host": host or "<unset>",
            "private_key": _mask(self.private_key),
            "contract_address": self.contract_address or "<unset>",
            "chain_id": self.chain_id,
            "evidence_base_url": self.evidence_base_url or "<unset>",
            "pinata_jwt": _mask(self.pinata_jwt),
        }
