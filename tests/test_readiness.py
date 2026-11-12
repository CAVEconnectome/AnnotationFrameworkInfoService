"""Tests for datasets/readiness.py: turning a datastack into one cross-service checklist.

The module is loaded by path so these tests need neither a database nor the app (and are immune
to model changes); outbound HTTP is replaced by a routing table of canned responses.
"""

import importlib.util
import pathlib
from types import SimpleNamespace

import pytest
import requests

PATH = pathlib.Path(__file__).resolve().parents[1] / "annotationinfoservice" / "datasets" / "readiness.py"
spec = importlib.util.spec_from_file_location("_readiness_under_test", PATH)
readiness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(readiness)

AUTH = "global.example.org/auth"
PCG = "https://local.example.org/segmentation"


def make_datastack(**overrides):
    fields = dict(
        name="test_ds",
        segmentation_source=f"graphene://{PCG}/table/test_graph",
        local_server="https://local.example.org",
        aligned_volume=SimpleNamespace(name="av", image_source="precomputed://gs://img-bucket/em"),
    )
    fields.update(overrides)
    return SimpleNamespace(**fields)


def pcg_report(status="ok", auth_server=AUTH):
    return {
        "service": "pychunkedgraph",
        "auth_server": auth_server,
        "status": status,
        "checks": [
            {"id": "pcg.mesh.dynamic_writable", "step": "infra", "status": status,
             "message": "m", "remediation": "r", "docs": ""},
        ],
    }


class Resp:
    def __init__(self, status_code, body=None):
        self.status_code = status_code
        self._body = body

    def json(self):
        return self._body


@pytest.fixture
def routes(monkeypatch):
    """url -> Resp (or Exception to raise). Unlisted urls 404."""
    table = {
        f"{PCG}/table/test_graph/readiness": Resp(200, pcg_report()),
        "https://storage.googleapis.com/img-bucket/em/info": Resp(200, {}),
        f"https://{AUTH}/api/v1/service/datastack/table/test_ds/dataset": Resp(200, "minnie"),
        f"https://{AUTH}/api/v1/service/aligned_volume/table/av/dataset": Resp(200, "minnie"),
        f"https://{AUTH}/api/v1/service/pychunkedgraph/table/test_graph/dataset": Resp(200, "minnie"),
    }
    seen_headers = []

    def fake_get(url, headers=None, timeout=None):
        seen_headers.append(headers)
        resp = table.get(url, Resp(404))
        if isinstance(resp, Exception):
            raise resp
        return resp

    monkeypatch.setattr(readiness.requests, "get", fake_get)
    monkeypatch.setattr(readiness, "AUTH_URL", AUTH)
    readiness._CACHE.clear()
    table["_headers"] = seen_headers
    return table


def checks_by_id(report):
    return {c["id"]: c for step in report["steps"] for c in step["checks"]}


def test_parse_segmentation_source():
    assert readiness.parse_segmentation_source(f"graphene://{PCG}/table/abc") == (PCG, "abc")
    assert readiness.parse_segmentation_source("precomputed://gs://b/seg") is None
    assert readiness.parse_segmentation_source(None) is None


def test_targets_for_graphene_datastack():
    table, targets = readiness.targets_for(make_datastack())
    assert table == "test_graph"
    assert targets["pychunkedgraph"] == f"{PCG}/table/test_graph/readiness"
    assert "materializationengine" in targets and "l2cache" in targets


def test_healthy_datastack(routes):
    report = readiness.collect(make_datastack(), "tok")
    checks = checks_by_id(report)
    assert checks["pcg.mesh.dynamic_writable"]["service"] == "pychunkedgraph"
    assert checks["auth.pcg_table.same_dataset"]["status"] == "ok"
    assert checks["auth.global_server.consistent"]["status"] == "ok"
    assert checks["info.image_source.readable"]["status"] == "ok"
    # l2cache and materialization have not adopted the contract: unknown, not failed.
    assert checks["l2cache.readiness"]["status"] == "unknown"
    assert report["status"] == "unknown"
    # The requesting admin's token is what gets forwarded.
    assert {"Authorization": "Bearer tok"} in routes["_headers"]


def test_steps_are_in_onboarding_order(routes):
    report = readiness.collect(make_datastack(), "tok")
    steps = [s["step"] for s in report["steps"]]
    assert steps == sorted(steps, key=readiness.STEPS.index)


def test_service_failures_propagate(routes):
    routes[f"{PCG}/table/test_graph/readiness"] = Resp(200, pcg_report(status="fail"))
    report = readiness.collect(make_datastack(), "tok")
    assert report["status"] == "fail"
    infra = next(s for s in report["steps"] if s["step"] == "infra")
    assert infra["status"] == "fail"


def test_unreachable_pcg_fails(routes):
    routes[f"{PCG}/table/test_graph/readiness"] = requests.ConnectionError("refused")
    checks = checks_by_id(readiness.collect(make_datastack(), "tok"))
    assert checks["pychunkedgraph.reachable"]["status"] == "fail"


def test_dataset_mismatch_between_pcg_and_datastack(routes):
    routes[f"https://{AUTH}/api/v1/service/pychunkedgraph/table/test_graph/dataset"] = Resp(200, "other")
    check = checks_by_id(readiness.collect(make_datastack(), "tok"))["auth.pcg_table.same_dataset"]
    assert check["status"] == "fail"
    assert "minnie" in check["remediation"]


def test_unmapped_pcg_table(routes):
    del routes[f"https://{AUTH}/api/v1/service/pychunkedgraph/table/test_graph/dataset"]
    check = checks_by_id(readiness.collect(make_datastack(), "tok"))["auth.pcg_table.same_dataset"]
    assert check["status"] == "fail"
    assert "not mapped" in check["message"]


def test_pcg_on_a_different_global_server(routes):
    routes[f"{PCG}/table/test_graph/readiness"] = Resp(200, pcg_report(auth_server="other.org/auth"))
    check = checks_by_id(readiness.collect(make_datastack(), "tok"))["auth.global_server.consistent"]
    assert check["status"] == "fail"


def test_precomputed_segmentation_skips_pcg(routes):
    ds = make_datastack(segmentation_source="precomputed://gs://b/seg")
    checks = checks_by_id(readiness.collect(ds, "tok"))
    assert checks["info.segmentation_source.parseable"]["status"] == "skip"
    assert not any(c.startswith("pcg.") for c in checks)
    assert "auth.pcg_table.same_dataset" not in checks


def test_private_image_source_warns(routes):
    routes["https://storage.googleapis.com/img-bucket/em/info"] = Resp(403)
    check = checks_by_id(readiness.collect(make_datastack(), "tok"))["info.image_source.readable"]
    assert check["status"] == "warn"


def test_reports_are_cached_until_refresh(routes, monkeypatch):
    calls = []
    real = readiness.collect
    monkeypatch.setattr(readiness, "collect", lambda *a, **k: calls.append(1) or real(*a, **k))
    ds = make_datastack()
    readiness.get_report(ds, "tok")
    readiness.get_reports([ds, ds], "tok")
    assert len(calls) == 1
    readiness.get_report(ds, "tok", refresh=True)
    assert len(calls) == 2


def test_templates_parse():
    jinja2 = pytest.importorskip("jinja2")
    templates = PATH.parents[1] / "templates"
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(templates)))
    for name in ("readiness.html", "readiness_overview.html", "base.html", "datastack.html"):
        env.parse(env.loader.get_source(env, name)[0])


def test_unmapped_aligned_volume(routes):
    del routes[f"https://{AUTH}/api/v1/service/aligned_volume/table/av/dataset"]
    check = checks_by_id(readiness.collect(make_datastack(), "tok"))["auth.aligned_volume.dataset_exists"]
    assert check["status"] == "fail"
    assert "(aligned_volume, av)" in check["remediation"]
