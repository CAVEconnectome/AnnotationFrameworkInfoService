# Import flask dependencies
from flask import Blueprint, jsonify, render_template, current_app
from annotationinfoservice.datasets.models import DataSet
from annotationinfoservice.datasets.schemas import DataSetSchema
import neuroglancer

mod_datasets = Blueprint('datasets', __name__, url_prefix='/datasets')


@mod_datasets.route("/")
def index():
    datasets = DataSet.query.all()
    return render_template('datasets.html', datasets=datasets)


@mod_datasets.route("/dataset/<datasetname>")
def dataset_view(datasetname):
    dataset = DataSet.query.filter(DataSet.name == datasetname).first_or_404()
    neuroglancer
    return render_template('dataset.html', dataset=dataset)


@mod_datasets.route("/api/")
def get_datasets():
    datasets = DataSet.query.all()
    return jsonify([d.name for d in datasets], many=True)


@mod_datasets.route("/api/<dataset>", methods=['GET'])
def get_dataset(dataset):
    dataset = DataSet.query.filter_by(name=dataset).first_or_404()
    schema = DataSetSchema()
    return schema.jsonify(dataset)
