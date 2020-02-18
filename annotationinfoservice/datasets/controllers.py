# Import flask dependencies
from flask import Blueprint, jsonify, render_template, current_app
from annotationinfoservice.datasets.models import DataSet
from annotationinfoservice.datasets.schemas import DataSetSchema, DataSetSchema2
import neuroglancer

mod_datasets = Blueprint('datasets', __name__, url_prefix='/datasets')

__version__ = "0.4.0"
@mod_datasets.route("/")
def index():
    datasets = DataSet.query.all()
    return render_template('datasets.html',
                            datasets=datasets,
                            version=__version__)

@mod_datasets.route("/dataset/<datasetname>")
def dataset_view(datasetname):
    dataset = DataSet.query.filter(DataSet.name == datasetname).first_or_404()
    state = neuroglancer.ViewerState()
    state.layers['img'] = neuroglancer.ImageLayer(source=dataset.image_path)
    state.layers['seg'] = neuroglancer.SegmentationLayer(source=dataset.segmentation_path)
    state.layers['ann'] = neuroglancer.AnnotationLayer()
    state.layout = "xy-3d"
    if dataset.viewer_site is not None:
        site = dataset.viewer_site
    else:
        site = current_app.config['NEUROGLANCER_URL']
    ng_url = neuroglancer.to_url(state,
                                 prefix=site)

    return render_template('dataset.html',
                            dataset=dataset,
                            ng_url=ng_url,
                            version=__version__)


@mod_datasets.route("/api/datasets")
def get_datasets():
    datasets = DataSet.query.all()
    return jsonify([d.name for d in datasets])


@mod_datasets.route("/api/dataset/<dataset>", methods=['GET'])
def get_dataset(dataset):
    dataset = DataSet.query.filter_by(name=dataset).first_or_404()
    schema = DataSetSchema()
    return schema.jsonify(dataset)

@mod_datasets.route("/api/v2/dataset/<dataset>", methods=['GET'])
def get_dataset_v2(dataset):
    dataset = DataSet.query.filter_by(name=dataset).first_or_404()
    schema = DataSetSchema2()
    return schema.jsonify(dataset)
