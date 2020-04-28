# Import flask dependencies
from flask import Blueprint, jsonify, render_template, current_app
from annotationinfoservice.datasets.models import DataSet, DataSetV2, PermissionGroup, TableMapping
from annotationinfoservice.datasets.schemas import DataSetSchema, DataSetSchemaV2, TableMappingSchema, PermissionGroupSchema
from nglui.statebuilder import *

mod_datasets = Blueprint('datasets', __name__, url_prefix='/datasets')

__version__ = "0.4.0"
@mod_datasets.route("/")
def index():
    datasets = DataSetV2.query.all()
    return render_template('datasets.html',
                            datasets=datasets,
                            version=__version__)

@mod_datasets.route("/dataset/<datasetname>")
def dataset_view(datasetname):
    dataset = DataSetV2.query.filter(DataSetV2.name == datasetname).first_or_404()
    
    img_layer = ImageLayerConfig(name='layer23',
                                    source=dataset.image_source,
                                    )
    # we want the segmentation layer with our target neuron always on
    seg_layer = SegmentationLayerConfig(name = 'seg',
                                        source=dataset.segmentation_source)
    ann_layer = AnnotationLayerConfig(name='ann')
                                
    # setup a state builder with this layer pipeline
    sb = StateBuilder([img_layer, seg_layer, ann_layer])
    
    if dataset.viewer_site is not None:
        site = dataset.viewer_site
    else:
        site = current_app.config['NEUROGLANCER_URL']
    ng_url=sb.render_state(return_as='url', url_prefix = site)

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

@mod_datasets.route("/api/v2/datasets")
def get_datasets_v2():
    datasets = DataSetV2.query.all()
    return jsonify([d.name for d in datasets])

@mod_datasets.route("/api/v2/dataset/<dataset>", methods=['GET'])
def get_dataset_v2(dataset):
    dataset = DataSetV2.query.filter_by(name=dataset).first_or_404()
    schema = DataSetSchemaV2()
    return schema.jsonify(dataset)

@mod_datasets.route("/api/v2/permissiongroups", methods=['GET'])
def get_permissiongroups():
    pgs = PermissionGroup.query.all()
    return jsonify([pg.name for pg in pgs])

@mod_datasets.route("/api/v2/permissiongroup/id/<pg_id>", methods=['GET'])
def get_permissiongroup_by_id(pg_id):
    pg = PermissionGroup.query.filter_by(id=pg_id).first_or_404()
    schema = PermissionGroupSchema()
    return schema.jsonify(pg)

@mod_datasets.route("/api/v2/permissiongroup/name/<pg_id>", methods=['GET'])
def get_permissiongroup_by_name(pg_name):
    pg = PermissionGroup.query.filter_by(name=pg_name).first_or_404()
    schema = PermissionGroupSchema()
    return schema.jsonify(pg)

@mod_datasets.route("/api/v2/tablemapping/service/<service_name>", methods=['GET'])
def get_tablemappings_from_service(service_name):
    tablemaps = TableMapping.query.filter_by(service_name=service_name).all()
    schema = TableMappingSchema()
    print(len(tablemaps))
    return schema.jsonify(tablemaps, many=True)

@mod_datasets.route("/api/v2/tablemapping/service/<service_name>/table/<table_name>", methods=['GET'])
def get_permission_group_from_table_and_service(service_name, table_name):

    tablemap = TableMapping.query.filter_by(table_name=table_name, service_name=service_name).first_or_404()
    return jsonify(tablemap.permissiongroup.name)
