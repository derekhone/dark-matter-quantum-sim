"""ProofRecord binding for the dark-matter-quantum-sim series.

Same structure and hashing discipline as the Remnant Fieldworks quantum
witness series (WITNESS / BELLWETHER / CHRONO / OMNI / TRINITY): every result
is serialized into a canonical JSON ProofRecord and bound to itself by a
SHA-256 hash computed over the record *without* the ``record_hash`` field.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict

SERIES = "dark-matter-quantum-sim"

HONEST_SCOPE = (
    "toy Hamiltonian classical simulation only; not detection of real dark "
    "matter"
)


def utc_now() -> str:
    """Return current UTC time as an ISO-8601 string with a Z suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _canonical_json(record: Dict[str, Any]) -> str:
    """Deterministic JSON serialization used for hashing (sorted keys)."""
    return json.dumps(record, sort_keys=True, separators=(",", ":"), default=_default)


def _default(obj: Any) -> Any:
    """JSON fallback for numpy scalars/arrays."""
    try:
        import numpy as np

        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
    except Exception:  # pragma: no cover - numpy always present here
        pass
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def compute_record_hash(record: Dict[str, Any]) -> str:
    """SHA-256 over the record with any existing ``record_hash`` removed."""
    payload = {k: v for k, v in record.items() if k != "record_hash"}
    canonical = _canonical_json(payload)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def make_proofrecord(
    experiment_id: str,
    model: str,
    parameters: Dict[str, Any],
    observable: str,
    result: Dict[str, Any],
    threshold: str,
    verdict: str,
    *,
    series: str = SERIES,
    honest_scope: str = HONEST_SCOPE,
    timestamp_utc: str | None = None,
) -> Dict[str, Any]:
    """Build a ProofRecord dict with a self-binding SHA-256 ``record_hash``."""
    record: Dict[str, Any] = {
        "experiment_id": experiment_id,
        "series": series,
        "model": model,
        "timestamp_utc": timestamp_utc or utc_now(),
        "parameters": parameters,
        "observable": observable,
        "result": result,
        "threshold": threshold,
        "verdict": verdict,
        "honest_scope": honest_scope,
    }
    record["record_hash"] = compute_record_hash(record)
    return record


def verify_record(record: Dict[str, Any]) -> bool:
    """Return True iff the stored ``record_hash`` matches a recomputation."""
    stored = record.get("record_hash")
    if not stored:
        return False
    return stored == compute_record_hash(record)


def save_record(record: Dict[str, Any], path: str) -> None:
    """Write a ProofRecord to disk as pretty JSON."""
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, default=_default)
        fh.write("\n")


def load_record(path: str) -> Dict[str, Any]:
    """Load a ProofRecord from disk."""
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


__all__ = [
    "SERIES",
    "HONEST_SCOPE",
    "utc_now",
    "compute_record_hash",
    "make_proofrecord",
    "verify_record",
    "save_record",
    "load_record",
]
