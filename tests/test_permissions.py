"""Tests for datasets/permissions.py: missing middle_auth mappings must not break pages.

Why this exists: adding a datastack (or aligned volume) to the info service without adding its
middle_auth table mapping made the dataset lookup raise, and because the list views check every
row, every user's datastack list and ngl_info broke. The datastack page also died inside
CAVEclient when the PCG table was unmapped.

These run against the real middle_auth_client (>= the table-mapping-errors release) with only the
auth server's HTTP calls faked. permissions.py is loaded by path, so no database or app is needed.
"""

import importlib.util
import pathlib
from types import SimpleNamespace

import pytest
import requests
from flask import Blueprint, Flask, g, render_template

middle_auth_client = pytest.importorskip("middle_auth_client")
if not hasattr(middle_auth_client, "filter_permitted"):
    pytest.skip(
        "needs middle_auth_client with table-mapping errors (CAVEconnectome/middle_auth_client#28)",
        allow_module_level=True,
    )
from middle_auth_client import decorators  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1] / "annotationinfoservice"
spec = importlib.util.spec_from_file_location(
    "_permissions_under_test", ROOT / "datasets" / "permissions.py"
)
permissions = importlib.util.module_from_spec(spec)
spec.loader.exec_module(permissions)

# (namespace, table) -> dataset. Missing -> 404. Exceptions are raised.
MAPPINGS = {}


class FakeResponse:
    def __init__(self, status_code, body=None):
        self.status_code = status_code
        self._body = body
        self.content = b""

    def json(self):
        return self._body


def fake_get(url, headers=None, timeout=None):
    _, _, path = url.partition("/api/v1/service/")
    namespace, _, rest = path.partition("/table/")
    value = MAPPINGS.get((namespace, rest[: -len("/dataset")]))
    if isinstance(value, Exception):
        raise value
    if value is None:
        return FakeResponse(404)
    return FakeResponse(200, value)


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setattr(decorators.session, "get", fake_get)
    decorators.dataset_from_table_id.cache_clear()
    MAPPINGS.clear()
    MAPPINGS.update(
        {
            ("datastack", "good"): "minnie",
            ("datastack", "secret"): "other",
            ("aligned_volume", "av"): "minnie",
        }
    )

    app = Flask(__name__, template_folder=str(ROOT / "templates"))
    app.config["AUTH_TOKEN"] = "service-token"
    bp = Blueprint("datastacks", __name__)
    for endpoint, rule in [
        ("index", "/"),
        ("readiness_overview", "/readiness"),
        ("datastack_readiness", "/datastack/<datastackname>/readiness"),
        ("datastack_view", "/datastack/<datastackname>"),
    ]:
        bp.add_url_rule(rule, endpoint, lambda **k: "")
    app.register_blueprint(bp, url_prefix="/info/datastacks")
    admin = Blueprint("admin", __name__)
    admin.add_url_rule("/", "index", lambda: "")
    app.register_blueprint(admin, url_prefix="/info/admin")
    app.add_url_rule(
        "/info/api/datastack/full/<datastack>",
        "api.Annotation Infoservice_data_stack_name_full_resource",
        lambda **k: "",
    )
    return app


def login(admin):
    g.auth_user = {"id": 1, "admin": admin, "permissions_v2": {"minnie": ["view"]}}
    g.auth_token = "user-token"


def stacks(*names):
    return [SimpleNamespace(name=n) for n in names]


def names(items):
    return [i.name for i in items]


def test_unmapped_datastack_is_hidden_from_users_without_error(app):
    with app.test_request_context():
        login(admin=False)
        shown = permissions.visible(stacks("good", "secret", "new"), "datastack", show_broken=True)
        assert names(shown) == ["good"]
        assert permissions.warning_headers() == {}


def test_admin_sees_unmapped_datastack_with_explanation(app):
    with app.test_request_context():
        login(admin=True)
        shown = permissions.visible(stacks("good", "secret", "new"), "datastack", show_broken=True)
        # "secret" is mapped but not permitted: still hidden, even from admins.
        assert names(shown) == ["good", "new"]
        (problem,) = permissions.problems()
        assert problem["table_id"] == "new" and problem["kind"] == "unmapped"
        assert "(datastack, new)" in problem["remediation"]
        assert problem["readiness_url"] == "/info/datastacks/datastack/new/readiness"
        assert permissions.broken("datastack") == {"new": "unmapped"}


def test_api_lists_drop_broken_rows_even_for_admins_but_say_so(app):
    with app.test_request_context():
        login(admin=True)
        assert names(permissions.visible(stacks("good", "new"), "datastack")) == ["good"]
        assert "datastack:new" in permissions.warning_headers()["X-CAVE-Warning"]


def test_unmapped_aligned_volume(app):
    with app.test_request_context():
        login(admin=False)
        assert names(permissions.visible(stacks("av", "new_av"), "aligned_volume")) == ["av"]


def test_auth_server_outage_is_no_permission_not_a_crash(app):
    MAPPINGS[("datastack", "good")] = requests.ConnectionError("auth down")
    with app.test_request_context():
        login(admin=True)
        assert permissions.visible(stacks("good"), "datastack") == []
        assert permissions.broken("datastack") == {"good": "auth_unavailable"}


def test_diagnose_datastack_finds_unmapped_pcg_table(app):
    ds = SimpleNamespace(name="good", aligned_volume=SimpleNamespace(name="av"))
    with app.test_request_context():
        login(admin=True)
        permissions.diagnose_datastack(ds, "minnie3_v1")
        (problem,) = permissions.problems()
        assert problem["namespace"] == "pychunkedgraph"
        assert "(pychunkedgraph, minnie3_v1)" in problem["remediation"]


def _datastack():
    return SimpleNamespace(
        name="good",
        description="d",
        local_server="https://local",
        skeleton_source=None,
        aligned_volume=SimpleNamespace(name="av"),
    )


def test_datastack_page_admin_notice(app):
    with app.test_request_context():
        login(admin=True)
        permissions.diagnose_datastack(_datastack(), "minnie3_v1")
        html = render_template(
            "datastack.html",
            datastack=_datastack(),
            is_admin=True,
            version="x",
            link_error="401 Client Error",
            problems=permissions.problems(),
        )
        assert "Admin notice" in html and "minnie3_v1" in html and "401 Client Error" in html
        assert "viewer link</a>" not in html


def test_datastack_page_user_sees_no_internals(app):
    with app.test_request_context():
        login(admin=False)
        html = render_template(
            "datastack.html",
            datastack=_datastack(),
            is_admin=False,
            version="x",
            link_error="401 Client Error",
            problems=[],
        )
        assert "temporarily unavailable" in html
        assert "401" not in html and "Admin notice" not in html


def test_datastack_list_marks_broken_rows_for_admin(app):
    MAPPINGS[("datastack", "flaky")] = requests.Timeout("slow")
    with app.test_request_context():
        login(admin=True)
        shown = permissions.visible(stacks("good", "new", "flaky"), "datastack", show_broken=True)
        html = render_template(
            "datastacks.html",
            datastacks=shown,
            problems=permissions.problems(),
            broken=permissions.broken("datastack"),
            is_admin=True,
            version="x",
        )
        assert html.count("not mapped in middle_auth") == 1
        assert html.count("auth lookup failed") == 1
