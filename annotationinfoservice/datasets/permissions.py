"""
Info-service glue for middle_auth_client's table-mapping handling.

middle_auth_client does the generic work: failed dataset lookups count as "no permission"
(`filter_permitted`) and are recorded per request (`auth_problems()`). This module adds the
pieces specific to the info service: showing broken rows to admins, linking problems to the
readiness checklist, diagnosing everything a datastack page depends on, and a warning header for
JSON list endpoints.
"""

from flask import current_app, g, url_for
from middle_auth_client import (
    TableMappingError,
    auth_problems,
    filter_permitted,
    is_global_admin,
    record_auth_problem,
)
from middle_auth_client.decorators import dataset_from_table_id

is_admin = is_global_admin


def _service_token():
    return current_app.config.get("AUTH_TOKEN") or g.get("auth_token") or ""


def problems():
    """This request's auth problems, each with a readiness link where one exists."""
    out = []
    for problem in auth_problems():
        problem = dict(problem)
        problem["readiness_url"] = None
        if problem["namespace"] == "datastack":
            try:
                problem["readiness_url"] = url_for(
                    "datastacks.datastack_readiness", datastackname=problem["table_id"]
                )
            except Exception:
                pass
        out.append(problem)
    return out


def broken(namespace):
    """{name: kind} for rows of `namespace` whose lookup failed during this request."""
    return {
        p["table_id"]: p["kind"] for p in auth_problems() if p["namespace"] == namespace
    }


def visible(
    items, namespace, permission="view", name=lambda item: item.name, show_broken=False
):
    """Filter `items` to what the user may see.

    With show_broken (HTML views), admins also see the rows whose lookup failed so they can find
    and fix them; the JSON endpoints leave them out so response bodies stay well-formed.
    """
    permitted = filter_permitted(
        items, permission, namespace, name=name, ignore_tos=True
    )
    if not (show_broken and is_admin()):
        return permitted
    shown = {name(item) for item in permitted} | set(broken(namespace))
    return [item for item in items if name(item) in shown]


def diagnose_datastack(datastack, pcg_table=None):
    """Record every mapping a datastack page depends on that cannot be resolved."""
    checks = [
        ("datastack", datastack.name),
        ("aligned_volume", datastack.aligned_volume.name),
    ]
    if pcg_table:
        checks.append(("pychunkedgraph", pcg_table))
    for namespace, name in checks:
        try:
            dataset_from_table_id(namespace, name, _service_token())
        except TableMappingError as e:
            record_auth_problem(e.to_problem())


def warning_headers():
    """For JSON endpoints: tell admins which rows were dropped, without changing the body."""
    if not is_admin() or not auth_problems():
        return {}
    names = ", ".join(f"{p['namespace']}:{p['table_id']}" for p in auth_problems())
    return {"X-CAVE-Warning": f"Hidden because their middle_auth lookup failed: {names}"}
