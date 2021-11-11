from flask import jsonify, render_template, current_app, make_response, Blueprint, g
from annotationinfoservice.datasets.service import (
    DataStackService,
    AlignedVolumeService,
)
from nglui.statebuilder import (
    ImageLayerConfig,
    SegmentationLayerConfig,
    AnnotationLayerConfig,
    StateBuilder,
)
from middle_auth_client import (
    auth_required,
    user_has_permission,
    auth_requires_permission,
)
import flask
import os

__version__ = "3.5.1"

views_bp = Blueprint("datastacks", __name__, url_prefix="/datastacks")


@views_bp.route("/")
@auth_required
def index():
    datastacks = DataStackService.get_all()
    datastacks = [
        d for d in datastacks if user_has_permission("view", d.name, "datastack")
    ]
    return render_template(
        "datastacks.html",
        datastacks=datastacks,
        is_admin=g.auth_user["admin"],
        user=g.auth_user["id"],
        logout_url=os.environ.get("STICKY_AUTH_URL", None) + "/api/v1/logout",
        version=__version__,
    )


@views_bp.route("/datastack/<datastackname>")
@auth_requires_permission(
    "view", table_arg="datastackname", resource_namespace="datastack"
)
def datastack_view(datastackname):
    datastack = DataStackService.get_datastack_by_name(datastackname)

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
    sb = StateBuilder([img_layer, seg_layer, ann_layer])

    if datastack.viewer_site is not None:
        site = datastack.viewer_site
    else:
        site = current_app.config["NEUROGLANCER_URL"]
    ng_url = sb.render_state(return_as="url", url_prefix=site)

    return render_template(
        "datastack.html",
        datastack=datastack,
        is_admin=g.auth_user["admin"],
        ng_url=ng_url,
        version=__version__,
    )
