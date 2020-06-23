from flask import jsonify, render_template, current_app, make_response, Blueprint
from annotationinfoservice.datasets.service import DataStackService, AlignedVolumeService
from nglui.statebuilder import ImageLayerConfig, SegmentationLayerConfig, AnnotationLayerConfig, StateBuilder


__version__ = "0.4.0"

views_bp = Blueprint('datastacks', __name__, url_prefix='/datastacks')


@views_bp.route("/")
def index():
    datastacks = DataStackService.get_all()
    return render_template('datastacks.html',
                            datastacks=datastacks,
                            version=__version__)


@views_bp.route("/datastack/<datastackname>")
def datastack_view(datastackname):
    datastack = DataStackService.get_datastack_by_name(datastackname)
    
    img_layer = ImageLayerConfig(name='layer23',
                                 source=datastack.image_source)
    # we want the segmentation layer with our target neuron always on
    seg_layer = SegmentationLayerConfig(name = 'seg',
                                        source=datastack.segmentation_source)
    ann_layer = AnnotationLayerConfig(name='ann')
                                
    # setup a state builder with this layer pipeline
    sb = StateBuilder([img_layer, seg_layer, ann_layer])
    
    if datastack.viewer_site is not None:
        site = datastack.viewer_site
    else:
        site = current_app.config['NEUROGLANCER_URL']
    ng_url=sb.render_state(return_as='url', url_prefix = site)

    return render_template('datastack.html',
                            datastack=datastack,
                            ng_url=ng_url,
                            version=__version__)

