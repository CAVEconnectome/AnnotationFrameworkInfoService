import requests
import os
import re

class InfoServiceClient(object):
    def __init__(self, endpoint, dataset_name=None):
        self.endpoint=endpoint
        self.dataset=dataset_name
        self.session=requests.Session()
        self.cached_data = dict()

    def get_datasets(self):
        url = '{}/api/datasets'.format(self.endpoint)
        response = self.session.get(url)
        assert(response.status_code == 200)
        return response.json()

    def get_dataset_info(self, dataset=None, use_stored=True):
        if dataset == None:
            dataset = self.dataset
        assert(dataset is not None)
        if (not use_stored) or (dataset not in self.cached_data):
            url='{}/api/dataset/{}'.format(self.endpoint, dataset)
            response = self.session.get(url)
            assert(response.status_code==200)
            self.cached_data[dataset]=response.json()
        return self.cached_data.get(dataset, None)

    def get_property(self, info_property, dataset=None, use_stored=True):
        if dataset == None:
            dataset=self.dataset
        assert(dataset is not None)
        self.get_dataset_info(dataset=dataset, use_stored=use_stored)
        return self.cached_data[dataset].get(info_property, None)

    def annotation_endpoint(self, dataset=None, use_stored=True):
        return self.get_property('annotation_engine_endpoint',
                                 dataset=dataset,
                                 use_stored=use_stored)

    def annotation_dataset_name(self, dataset=None, use_stored=True):
        return self.get_property('annotation_dataset_name',
                                 dataset=dataset,
                                 use_stored=use_stored)

    def flat_segmentation_source(self, dataset=None, use_stored=True):
        return self.get_property('flat_segmentation_source',
                                 dataset=dataset,
                                 use_stored=use_stored)

    def image_source(self, dataset=None, use_stored=True):
        return self.get_property('image_source',
                                 dataset=dataset,
                                 use_stored=use_stored)

    def pychunkgraph_endpoint(self, dataset=None, use_stored=True):
        return self.get_property('pychunkgraph_endpoint',
                                 dataset=dataset,
                                 use_stored=use_stored)

    def pychunkgraph_segmentation_source(self, dataset=None, use_stored=True):
        return self.get_property('pychunkgraph_segmentation_source',
                                 dataset=dataset,
                                 use_stored=use_stored)

    def refresh_stored_data(self):
        for ds in self.cached_data.keys():
            self.get_dataset_info(dataset=ds, use_stored=False)

    def neuroglancer_link(self, dataset=None):
        if dataset == None:
            dataset=self.dataset
        assert(dataset is not None)
        url = '{}/dataset/{}'.format(self.endpoint, dataset)
        response = self.session.get(url)
        assert(response.status_code == 200)

        qry_str='<a href = (?P<ng_link>https?\:.*)>viewer link<\/a>'
        qry = re.search(qry_str, response.content.decode())
        if qry is not None:
            ng_url = qry.groupdict().get('ng_link', None)
        else:
            ng_url = None
        return ng_url