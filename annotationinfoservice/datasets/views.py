from flask import jsonify, render_template, current_app, make_response, Blueprint
from annotationinfoservice.datasets.models import DataSet, DataSetV2, PermissionGroup, TableMapping


__version__ = "0.4.0"

views_bp = Blueprint('datasets', __name__, url_prefix='/datasets')


@views_bp.route("/")
def index():
    datasets = DataSetV2.query.all()
    return render_template('datasets.html',
                            datasets=datasets,
                            version=__version__)


# @views_bp.route("/dataset/<datasetname>")
# def dataset_view(datasetname):
#     dataset = DataSetV2.query.filter(DataSetV2.name == datasetname).first_or_404()
#     state = neuroglancer.ViewerState()
#     state.layers['img'] = neuroglancer.ImageLayer(source=dataset.image_path)
#     state.layers['seg'] = neuroglancer.SegmentationLayer(source=dataset.segmentation_path)
#     state.layers['ann'] = neuroglancer.AnnotationLayer()
#     state.layout = "xy-3d"
#     if dataset.viewer_site is not None:
#         site = dataset.viewer_site
#     else:
#         site = current_app.config['NEUROGLANCER_URL']
#     ng_url = neuroglancer.to_url(state,
#                                  prefix=site)

#     return render_template('dataset.html',
#                             dataset=dataset,
#                             ng_url=ng_url,
#                             version=__version__)

