"""Tests for the ProofRecord schema and hashing discipline."""

import json

from dm_sim.proofrecord import (
    HONEST_SCOPE,
    SERIES,
    compute_record_hash,
    make_proofrecord,
    verify_record,
)


def _sample():
    return make_proofrecord(
        experiment_id="DM-001-classical-v1",
        model="axion_pq_potential",
        parameters={"omega_0": 1.0, "lambda": 0.3},
        observable="sigma_z_expectation",
        result={"measured_period": 6.28, "target_period": 6.283},
        threshold="T within 5% of 2*pi/omega_0",
        verdict="PASS",
        timestamp_utc="2026-08-01T00:00:00Z",
    )


def test_record_has_required_fields():
    r = _sample()
    for key in (
        "experiment_id",
        "series",
        "model",
        "timestamp_utc",
        "parameters",
        "observable",
        "result",
        "threshold",
        "verdict",
        "honest_scope",
        "record_hash",
    ):
        assert key in r
    assert r["series"] == SERIES
    assert r["honest_scope"] == HONEST_SCOPE


def test_hash_is_deterministic():
    r1 = _sample()
    r2 = _sample()
    assert r1["record_hash"] == r2["record_hash"]


def test_hash_excludes_record_hash_field():
    r = _sample()
    recomputed = compute_record_hash(r)
    assert recomputed == r["record_hash"]


def test_verify_record_true():
    r = _sample()
    assert verify_record(r) is True


def test_verify_record_detects_tampering():
    r = _sample()
    r["verdict"] = "FAIL"  # tamper without recomputing hash
    assert verify_record(r) is False


def test_record_is_json_serializable():
    r = _sample()
    s = json.dumps(r)
    assert "record_hash" in s


def test_hash_changes_with_parameters():
    r1 = _sample()
    r2 = make_proofrecord(
        experiment_id="DM-001-classical-v1",
        model="axion_pq_potential",
        parameters={"omega_0": 2.0, "lambda": 0.3},
        observable="sigma_z_expectation",
        result={"measured_period": 6.28, "target_period": 6.283},
        threshold="T within 5% of 2*pi/omega_0",
        verdict="PASS",
        timestamp_utc="2026-08-01T00:00:00Z",
    )
    assert r1["record_hash"] != r2["record_hash"]
