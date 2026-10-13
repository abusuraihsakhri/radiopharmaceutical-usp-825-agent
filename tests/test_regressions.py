"""Regression coverage for batch CSV parsing, API error handling and honest mock behavior."""
import csv
import pytest

from cli import main as cli_main
from usp_825_nuclear.cli import main as nuclear_main
from agents.base import AuditTrail, SecurityException
from agents.llm_factory import LLMFactory


@pytest.mark.parametrize("runner,status_column", [
    (cli_main, "overall_urgency"), (nuclear_main, "overall_status")
])
def test_batch_false_flag_stays_false(tmp_path, runner, status_column):
    source = tmp_path / "in.csv"
    target = tmp_path / "out.csv"
    source.write_text(
        "task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor\n"
        "T-1,S-1,10,2,False,NOMINAL\n"
        "T-2,S-2,10,2,True,NOMINAL\n", encoding="utf-8")
    assert runner(["batch", "-i", str(source), "-o", str(target)]) == 0
    with target.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert rows[0][status_column] in {"ROUTINE", "NOMINAL_OPTIMAL"}
    assert rows[1][status_column] in {"CRITICAL_STAT_PANIC", "CRITICAL_INTERVENTION_REQUIRED"}


@pytest.mark.parametrize("runner", [cli_main,nuclear_main])
def test_batch_invalid_flag_fails_closed(tmp_path, runner):
    source = tmp_path / "in.csv"
    source.write_text("task_id,target_identifier,primary_metric,is_critical_flag\nT-1,S-1,10,possibly\n",encoding="utf-8")
    with pytest.raises(ValueError,match="Invalid is_critical_flag"):
        runner(["batch","-i",str(source),"-o",str(tmp_path / "out.csv")])


def test_mock_provider_cannot_claim_verification():
    response = LLMFactory.create("mock").invoke("What is this tool?")
    assert "No scientific verification" in response
    with pytest.raises(ValueError,match="not implemented"):
        LLMFactory.create("openai")


def test_audit_public_view_is_defensive_copy():
    trail = AuditTrail(secret_key="tests-only-secret-key-123")
    trail.log("a","b","c",{"x":"demo"})
    trail.get_trail()[0]["actor"] = "tampered-copy"
    assert trail.verify_integrity()


def test_api_validation_does_not_echo_sensitive_input():
    from fastapi.testclient import TestClient
    from agents.api import app
    client = TestClient(app)
    response = client.post("/api/audit",json={
       "task_id":"DEMO-1", "target_identifier":"SAMPLE-1",
       "primary_metric":"patient@example.com"
    })
    assert response.status_code == 422
    assert "patient@example.com" not in response.text


def test_api_blocks_identifiers_in_nested_attributes():
    from fastapi.testclient import TestClient
    from agents.api import app
    client = TestClient(app)
    response = client.post("/api/audit",json={
       "task_id":"DEMO-1", "target_identifier":"SAMPLE-1",
       "primary_metric":1, "attributes":{"notes":["MRN-12345678"]}
    })
    assert response.status_code == 422


def test_api_serves_browser_console():
    from fastapi.testclient import TestClient
    from agents.api import app
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "Not a USP" in response.text
    assert client.get("/demo-engine.js").status_code == 200

def test_concurrent_audit_logging_is_consistent():
    from concurrent.futures import ThreadPoolExecutor
    trail = AuditTrail(secret_key="tests-only-secret-key-123")
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda i: trail.log("actor","tier","EVENT",{"index":i}), range(100)))
    assert len(trail.get_trail()) == 100
    assert len({x["audit_id"] for x in trail.get_trail()}) == 100
    assert trail.verify_integrity()


def test_simulation_input_validation():
    from simulator import run_simulation
    with pytest.raises(ValueError, match="positive"):
        run_simulation(0, 1)
    with pytest.raises(ValueError, match="positive"):
        run_simulation(1, 0)


def test_domain_api_rejects_nested_phi():
    from fastapi.testclient import TestClient
    from usp_825_nuclear.server import create_app
    client = TestClient(create_app())
    response = client.post("/api/audit", json={"task_id":"DEMO-1","target_identifier":"SAMPLE-1","attributes":{"note":"MRN-12345678"}})
    assert response.status_code == 422
