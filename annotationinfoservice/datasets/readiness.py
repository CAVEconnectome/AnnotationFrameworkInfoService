"""
Datastack readiness aggregation.

Every CAVE service reports its own readiness for a table at `.../readiness` (checks run with the
service's own identity, so they catch IAM gaps). This module finds those endpoints from a
datastack's fields, calls them in parallel, and adds the checks that span services, e.g. that the
PCG table and the datastack belong to the same auth dataset. The result is one checklist grouped
by onboarding step.

Kept free of app/model imports so it can be tested without a database.
"""

import os
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from types import SimpleNamespace
from urllib.parse import urlparse

import requests

STEPS = ("ingest", "meshing", "infra", "auth", "info", "l2cache", "materialization")
OK, WARN, FAIL, SKIP, UNKNOWN = "ok", "warn", "fail", "skip", "unknown"
SEVERITY = {FAIL: 4, WARN: 3, UNKNOWN: 2, OK: 1, SKIP: 0}

HTTP_TIMEOUT = 10
CACHE_TTL = int(os.environ.get("READINESS_CACHE_TTL", "300"))
AUTH_URL = os.environ.get("AUTH_URL", os.environ.get("AUTH_URI", ""))

# graphene://https://host/segmentation/table/<table_id>  (prefix before /table is kept as the base)
GRAPHENE_RE = re.compile(r"^graphene://(https?://.+?)/table/([^/?#]+)")


def _check(check_id, step, status, message="", remediation="", service="infoservice"):
    return {
        "id": check_id,
        "step": step,
        "status": status,
        "message": message,
        "remediation": remediation,
        "docs": "",
        "service": service,
    }


def worst(statuses):
    statuses = list(statuses)
    if not statuses:
        return SKIP
    return max(statuses, key=lambda s: SEVERITY.get(s, 0))


def _host(url):
    if not url:
        return ""
    if "://" not in url:
        url = "https://" + url
    return urlparse(url).netloc


def parse_segmentation_source(source):
    """Returns (pcg_base_url, table_id), or None if not a graphene source."""
    if not source:
        return None
    match = GRAPHENE_RE.match(source)
    if match is None:
        return None
    return match.group(1), match.group(2)


def _bearer(token):
    return {"Authorization": f"Bearer {token}"} if token else {}


# ------------------------------------------------------------------- remote service reports


def fetch_service_report(service, url, token):
    """GET a service readiness endpoint and return its checks, tagged with `service`.

    A 404 means the service does not implement readiness yet; it is reported as unknown so
    services can adopt the contract one at a time.
    """
    try:
        resp = requests.get(url, headers=_bearer(token), timeout=HTTP_TIMEOUT)
    except requests.RequestException as e:
        return None, [
            _check(
                f"{service}.reachable",
                "info",
                FAIL,
                f"{service} unreachable at {url}: {e}",
                "Check that the service is deployed on this datastack's local_server.",
                service=service,
            )
        ]
    if resp.status_code == 404:
        return None, [
            _check(
                f"{service}.readiness",
                "info",
                UNKNOWN,
                f"{service} does not report readiness yet ({url} returned 404)",
                service=service,
            )
        ]
    if resp.status_code in (401, 403):
        return None, [
            _check(
                f"{service}.readiness",
                "info",
                UNKNOWN,
                f"Not authorized to read {service} readiness ({resp.status_code}); "
                "requires a global admin",
                service=service,
            )
        ]
    if resp.status_code != 200:
        return None, [
            _check(
                f"{service}.readiness",
                "info",
                FAIL,
                f"{service} readiness returned {resp.status_code}",
                service=service,
            )
        ]
    report = resp.json()
    checks = []
    for c in report.get("checks", []):
        c = dict(c)
        c.setdefault("service", service)
        checks.append(c)
    return report, checks


# ------------------------------------------------------------------- cross-service checks


def check_image_source(image_source):
    """The aligned volume's image info must be fetchable over http(s)."""
    if not image_source:
        return _check("info.image_source.readable", "info", FAIL, "No image source set")
    path = re.sub(r"^\w+://(?=\w+://)", "", image_source)  # drop precomputed:// etc.
    if path.startswith("gs://"):
        path = "https://storage.googleapis.com/" + path[len("gs://"):]
    if not path.startswith(("http://", "https://")):
        return _check(
            "info.image_source.readable",
            "info",
            SKIP,
            f"Cannot verify {image_source} from the info service",
        )
    url = path.rstrip("/") + "/info"
    try:
        resp = requests.get(url, timeout=HTTP_TIMEOUT)
    except requests.RequestException as e:
        return _check("info.image_source.readable", "info", FAIL, f"{url}: {e}")
    if resp.status_code == 200:
        return _check("info.image_source.readable", "info", OK, f"Read {url}")
    if resp.status_code in (401, 403):
        return _check(
            "info.image_source.readable",
            "info",
            WARN,
            f"{url} is not public ({resp.status_code}); viewers need their own credentials",
        )
    return _check(
        "info.image_source.readable",
        "info",
        FAIL,
        f"{url} returned {resp.status_code}",
        "Fix the aligned volume image_source in the info service admin.",
    )


def lookup_dataset(namespace, table, token, auth_url=None):
    """Return (dataset, error). dataset is None if unmapped."""
    auth_url = auth_url or AUTH_URL
    url = f"https://{auth_url}/api/v1/service/{namespace}/table/{table}/dataset"
    try:
        resp = requests.get(url, headers=_bearer(token), timeout=HTTP_TIMEOUT)
    except requests.RequestException as e:
        return None, f"auth server unreachable: {e}"
    if resp.status_code == 200:
        return resp.json(), None
    if resp.status_code == 404:
        return None, None
    return None, f"auth server returned {resp.status_code}"


def auth_checks(datastack_name, pcg_table, pcg_report, token, auth_url=None):
    auth_url = auth_url or AUTH_URL
    checks = []
    ds_dataset, err = lookup_dataset("datastack", datastack_name, token, auth_url)
    if err:
        checks.append(_check("auth.datastack.dataset_exists", "auth", FAIL, err))
    elif ds_dataset is None:
        checks.append(
            _check(
                "auth.datastack.dataset_exists",
                "auth",
                FAIL,
                f"Datastack '{datastack_name}' is not mapped to a dataset on {auth_url}",
                f"Add a service table mapping (datastack, {datastack_name}) -> <dataset> "
                "in middle_auth.",
            )
        )
    else:
        checks.append(
            _check(
                "auth.datastack.dataset_exists",
                "auth",
                OK,
                f"Datastack is in dataset '{ds_dataset}'",
            )
        )

    if pcg_table is None:
        return checks

    pcg_dataset, err = lookup_dataset("pychunkedgraph", pcg_table, token, auth_url)
    if err:
        checks.append(_check("auth.pcg_table.same_dataset", "auth", FAIL, err))
    elif pcg_dataset is None:
        checks.append(
            _check(
                "auth.pcg_table.same_dataset",
                "auth",
                FAIL,
                f"PCG table '{pcg_table}' is not mapped to a dataset",
                f"Add a service table mapping (pychunkedgraph, {pcg_table}) -> "
                f"{ds_dataset or '<dataset>'} in middle_auth.",
            )
        )
    elif ds_dataset is not None and pcg_dataset != ds_dataset:
        checks.append(
            _check(
                "auth.pcg_table.same_dataset",
                "auth",
                FAIL,
                f"PCG table is in dataset '{pcg_dataset}' but the datastack is in "
                f"'{ds_dataset}'; users can see one but not edit the other",
                f"Remap (pychunkedgraph, {pcg_table}) to '{ds_dataset}' in middle_auth, "
                "or move the datastack.",
            )
        )
    else:
        checks.append(
            _check(
                "auth.pcg_table.same_dataset",
                "auth",
                OK,
                f"PCG table is in dataset '{pcg_dataset}'",
            )
        )

    if pcg_report is not None:
        pcg_auth = pcg_report.get("auth_server", "")
        if not pcg_auth:
            checks.append(
                _check(
                    "auth.global_server.consistent",
                    "auth",
                    UNKNOWN,
                    "PCG did not report its auth server",
                )
            )
        elif _host(pcg_auth) != _host(auth_url):
            checks.append(
                _check(
                    "auth.global_server.consistent",
                    "auth",
                    FAIL,
                    f"PCG authenticates against {pcg_auth}, the info service against {auth_url}",
                    "Point the PCG deployment's AUTH_URI at this datastack's global server.",
                )
            )
        else:
            checks.append(
                _check(
                    "auth.global_server.consistent",
                    "auth",
                    OK,
                    f"Both use {auth_url}",
                )
            )
    return checks


# ------------------------------------------------------------------- aggregation


def snapshot(datastack):
    """Copy the fields readiness needs off an ORM DataStack.

    Reports are collected on worker threads, where lazy-loading `aligned_volume` would run
    outside the app context.
    """
    return SimpleNamespace(
        name=datastack.name,
        segmentation_source=datastack.segmentation_source,
        local_server=datastack.local_server,
        aligned_volume=SimpleNamespace(image_source=datastack.aligned_volume.image_source),
    )


def targets_for(datastack):
    """Map a datastack to the service readiness endpoints it depends on.

    Returns (pcg_table, {service: url}).
    """
    targets = {}
    pcg_table = None
    parsed = parse_segmentation_source(datastack.segmentation_source)
    if parsed is not None:
        pcg_base, pcg_table = parsed
        targets["pychunkedgraph"] = f"{pcg_base}/table/{pcg_table}/readiness"
        local = (datastack.local_server or "").rstrip("/")
        if local:
            targets["l2cache"] = f"{local}/l2cache/api/v1/table/{pcg_table}/readiness"
    local = (datastack.local_server or "").rstrip("/")
    if local:
        targets["materializationengine"] = (
            f"{local}/materialize/api/v3/datastack/{datastack.name}/readiness"
        )
    return pcg_table, targets


def collect(datastack, token, auth_url=None):
    """Full readiness report for one datastack."""
    checks = []
    pcg_table, targets = targets_for(datastack)

    if datastack.segmentation_source and pcg_table is None:
        checks.append(
            _check(
                "info.segmentation_source.parseable",
                "info",
                SKIP,
                f"Not a graphene source ({datastack.segmentation_source}); PCG checks skipped",
            )
        )
    elif pcg_table is None:
        checks.append(
            _check(
                "info.segmentation_source.parseable",
                "info",
                FAIL,
                "Datastack has no segmentation_source",
            )
        )
    else:
        checks.append(
            _check(
                "info.segmentation_source.parseable",
                "info",
                OK,
                f"PCG table '{pcg_table}'",
            )
        )

    with ThreadPoolExecutor(max_workers=len(targets) + 1) as pool:
        image = pool.submit(check_image_source, datastack.aligned_volume.image_source)
        futures = {
            service: pool.submit(fetch_service_report, service, url, token)
            for service, url in targets.items()
        }
        reports = {}
        for service, future in futures.items():
            report, service_checks = future.result()
            reports[service] = report
            checks.extend(service_checks)
        checks.append(image.result())

    checks.extend(
        auth_checks(
            datastack.name, pcg_table, reports.get("pychunkedgraph"), token, auth_url
        )
    )

    order = {step: i for i, step in enumerate(STEPS)}
    checks.sort(key=lambda c: order.get(c["step"], len(STEPS)))
    by_step = {}
    for c in checks:
        by_step.setdefault(c["step"], []).append(c)
    return {
        "datastack": datastack.name,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "status": worst(c["status"] for c in checks),
        "steps": [
            {"step": step, "status": worst(c["status"] for c in items), "checks": items}
            for step, items in by_step.items()
        ],
    }


_CACHE = {}
_CACHE_LOCK = threading.Lock()


def get_report(datastack, token, refresh=False, auth_url=None):
    """`collect` with a per-process TTL cache, so pages re-render without re-probing services."""
    now = time.monotonic()
    if not refresh:
        with _CACHE_LOCK:
            hit = _CACHE.get(datastack.name)
        if hit is not None and hit[0] > now:
            return hit[1]
    report = collect(datastack, token, auth_url=auth_url)
    with _CACHE_LOCK:
        _CACHE[datastack.name] = (now + CACHE_TTL, report)
    return report


def get_reports(datastacks, token, refresh=False, auth_url=None):
    """Reports for many datastacks, collected in parallel."""
    with ThreadPoolExecutor(max_workers=8) as pool:
        return list(
            pool.map(
                lambda d: get_report(d, token, refresh=refresh, auth_url=auth_url),
                datastacks,
            )
        )
