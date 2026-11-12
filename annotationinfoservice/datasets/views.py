from flask import jsonify, render_template, current_app, make_response, Blueprint, g
from annotationinfoservice.datasets.service import (
    DataStackService,
    AlignedVolumeService,
)
from annotationinfoservice.datasets.base_spelunker import spelunker_state
from nglui.statebuilder import (
    ImageLayerConfig,
    SegmentationLayerConfig,
    AnnotationLayerConfig,
    StateBuilder,
)
from middle_auth_client import (
    auth_required,
    auth_requires_admin,
    auth_requires_permission,
)
from annotationinfoservice.datasets import permissions, readiness
from caveclient import CAVEclient
import flask
import os
import numpy as np

__version__ = "4.3.3"

views_bp = Blueprint("datastacks", __name__, url_prefix="/datastacks")


@views_bp.route("/")
@auth_required
def index():
    datastacks = permissions.visible(
        DataStackService.get_all(), "datastack", show_broken=True
    )
    return render_template(
        "datastacks.html",
        datastacks=datastacks,
        problems=permissions.problems(),
        broken=permissions.broken("datastack"),
        is_admin=g.auth_user["admin"],
        user=g.auth_user["id"],
        logout_url=os.environ.get("STICKY_AUTH_URL", None) + "/api/v1/logout",
        version=__version__,
    )


@views_bp.route("/version")
def get_version():
    "Get version string"
    return jsonify(__version__)


def _refresh_requested():
    return flask.request.args.get("refresh", "false").lower() in ("1", "true", "yes")


# Readiness pages are global-admin only: they expose bucket paths and auth configuration, and
# they must work for datastacks whose auth mapping is still missing.
@views_bp.route("/readiness")
@auth_requires_admin
def readiness_overview():
    datastacks = [readiness.snapshot(d) for d in DataStackService.get_all()]
    reports = readiness.get_reports(
        datastacks, g.auth_token, refresh=_refresh_requested()
    )
    reports.sort(key=lambda r: r["datastack"])
    return render_template(
        "readiness_overview.html",
        reports=reports,
        steps=readiness.STEPS,
        is_admin=True,
        version=__version__,
    )


@views_bp.route("/datastack/<datastackname>/readiness")
@auth_requires_admin
def datastack_readiness(datastackname):
    datastack = readiness.snapshot(DataStackService.get_datastack_by_name(datastackname))
    report = readiness.get_report(datastack, g.auth_token, refresh=_refresh_requested())
    return render_template(
        "readiness.html",
        report=report,
        is_admin=True,
        version=__version__,
    )


@views_bp.route("/datastack/<datastackname>")
@auth_requires_permission(
    "view",
    table_arg="datastackname",
    resource_namespace="datastack",
    on_unmapped="admin_passthrough",
)
def datastack_view(datastackname):
    datastack = DataStackService.get_datastack_by_name(datastackname)
    links, link_error = {}, None
    try:
        links = _viewer_links(datastack)
    except Exception as e:
        current_app.logger.exception(f"Failed to build viewer links for {datastackname}")
        link_error = str(e)
        if permissions.is_admin():
            parsed = readiness.parse_segmentation_source(datastack.segmentation_source)
            permissions.diagnose_datastack(datastack, parsed[1] if parsed else None)

    return render_template(
        "datastack.html",
        datastack=datastack,
        is_admin=g.auth_user["admin"],
        link_error=link_error,
        problems=permissions.problems(),
        version=__version__,
        **links,
    )


def _viewer_links(datastack):
    """Viewer URLs for the datastack page.

    Goes through CAVEclient, i.e. back through this info service and the PCG, so it fails whenever
    the datastack or its PCG table is missing an auth mapping.
    """
    datastackname = datastack.name
    if datastack.viewer_resolution_x is not None:
        resolution = [
            datastack.viewer_resolution_x,
            datastack.viewer_resolution_y,
            datastack.viewer_resolution_z,
        ]
    else:
        resolution = [4, 4, 40]

    client = CAVEclient(
        datastackname,
        auth_token=g.auth_token,
        server_address=os.environ.get("GLOBAL_SERVER", None),
    )
    if datastack.base_link_id is not None:
        base_state = client.state.get_state_json(datastack.base_link_id)
    else:
        base_state = None

    img_layer = ImageLayerConfig(
        name="img",
        source=datastack.aligned_volume.image_source,
        contrast_controls=True,
        black=0.0,
        white=1.0,
    )
    # we want the segmentation layer with our target neuron always on
    seg_layer = SegmentationLayerConfig(
        name="seg", source=datastack.segmentation_source
    )
    ann_layer = AnnotationLayerConfig(name="ann")

    # setup a state builder with this layer pipeline
    sb = StateBuilder(
        [img_layer, seg_layer, ann_layer],
        base_state=base_state,
        resolution=resolution,
        client=client,
    )
    if datastack.segmentation_source.startswith("graphene://"):
        new_source = datastack.segmentation_source.replace(
            "https://", "middleauth+https://"
        )
    else:
        new_source = datastack.segmentation_source

    # seg_layer2 = SegmentationLayerConfig(name="seg", source=new_source)
    # sb2 = StateBuilder(
    #     [img_layer, seg_layer2, ann_layer],
    #     base_state=base_state,
    #     resolution=resolution,
    #     client=client,
    # )
    # ng_url2 = sb2.render_state(return_as="url", url_prefix=site2)

    if datastack.viewer_site is not None:
        site = datastack.viewer_site
    else:
        site = current_app.config["NEUROGLANCER_URL"]
    scaling = (
        np.array(client.chunkedgraph.segmentation_info["scales"][0]["resolution"])
        / client.info.viewer_resolution()
    )

    ctr = (
        np.array(
            client.chunkedgraph.segmentation_info["scales"][0].get(
                "voxel_offset", [0, 0, 0]
            )
        )
        * scaling
        + np.array(client.chunkedgraph.segmentation_info["scales"][0]["size"])
        * scaling
        / 2
    )
    viewer_resolution = client.info.viewer_resolution()
    spelunker_state["dimensions"]["x"][0] = float(viewer_resolution[0])
    spelunker_state["dimensions"]["y"][0] = float(viewer_resolution[1])
    spelunker_state["dimensions"]["z"][0] = float(viewer_resolution[2])
    spelunker_state["position"] = ctr.tolist()
    spelunker_image_source = datastack.aligned_volume.image_source
    if spelunker_image_source.startswith("graphene://"):
        spelunker_image_source = spelunker_image_source.replace(
            "https://", "middleauth+https://"
        )
        spelunker_image_source = spelunker_image_source.replace(
            "graphene://", "precomputed://"
        )

    spelunker_state["layers"][0]["source"] = spelunker_image_source
    spelunker_state["layers"][1]["source"] = new_source

    if datastack.skeleton_source is not None:
        skeleton_source = datastack.skeleton_source.replace(
            "precomputed://https://", "precomputed://middleauth+https://"
        )
        spelunker_state["layers"][1]["source"] = [
            {
                "url": new_source,
                "subsources": {
                    "default": True,
                    "graph": True,
                    "bounds": True,
                    "mesh": True,
                },
                "enableDefaultSubsources": False,
            },
            {
                "url": skeleton_source,
                "subsources": {"default": True},
                "enableDefaultSubsources": False,
            },
        ]

    cave_site = "https://ngl.cave-explorer.org/"
    state_id = client.state.upload_state_json(spelunker_state)
    cave_explorer_url = client.state.build_neuroglancer_url(
        state_id, cave_site
    ).replace("/?json_url=", "#!middleauth+")
    spelunker_site = "https://spelunker.cave-explorer.org/"
    spelunker_url = client.state.build_neuroglancer_url(
        state_id, spelunker_site
    ).replace("/?json_url=", "#!middleauth+")

    ng_url = sb.render_state(return_as="url", url_prefix=site)

    return dict(
        ng_url=ng_url,
        cave_explorer_url=cave_explorer_url,
        spelunker_url=spelunker_url,
    )
