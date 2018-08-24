# This file is part of the Etsin harvester service
#
# Copyright 2017-2018 Ministry of Education and Culture, Finland
#
# :author: CSC - IT Center for Science Ltd., Espoo Finland <servicedesk@csc.fi>
# :license: GNU Affero General Public License version 3

import os
import requests
from requests import exceptions, put, post, head
import json
from pylons import config
import logging

from .utils import str_to_bool

log = logging.getLogger(__name__)


class DataCatalogMetaxAPIService:

    METAX_HOST = config.get('metax.host')
    METAX_DATA_CATALOG_API_POST_URL = 'https://{0}/rest/datacatalogs'.format(METAX_HOST)
    METAX_DATA_CATALOG_DETAIL_URL = METAX_DATA_CATALOG_API_POST_URL + '/{id}'

    def __init__(self):
        self.api_user = config.get('metax.api_user')
        self.api_password = config.get('metax.api_password')
        self.verify = str_to_bool(config.get('metax.verify_ssl'))

    def create_data_catalog(self, data_catalog_json_filename):
        if not data_catalog_json_filename:
            log.error("No data catalog json filename given, unable to create data catalog to Metax")
            return None

        catalog = self.get_data_catalog_from_file(data_catalog_json_filename)
        log.info("Creating data catalog to Metax..")
        try:
            response_text = self._do_post_request(self.METAX_DATA_CATALOG_API_POST_URL, catalog, self.api_user,
                                                  self.api_password)
            data_catalog_id = json.loads(response_text)['catalog_json']['identifier']
            log.info("Data catalog created to Metax with identifier: {0}".format(data_catalog_id))
            return True
        except exceptions.HTTPError as e:
            log.error(e)
            log.error("Creating data catalog failed for some reason most likely in Metax data catalog API")
        return False

    def update_data_catalog_to_metax(self, data_catalog_json_filename):
        if not data_catalog_json_filename:
            log.error("No data catalog json filename given for updating data catalog")
            return False

        data_catalog_id = self.get_data_catalog_id_from_file(data_catalog_json_filename)
        data_catalog = self.get_data_catalog_from_file(data_catalog_json_filename)
        log.info("Updating data catalog to Metax..")
        try:
            self._do_put_request(self.METAX_DATA_CATALOG_DETAIL_URL.format(id=data_catalog_id), data_catalog,
                                 self.api_user, self.api_password)
            log.info("Data catalog updated to Metax with identifier: {id}".format(id=data_catalog_id))
        except exceptions.HTTPError as e:
            log.error(e)
            log.error("Updating data catalog failed for some reason most likely in Metax data catalog API")
            return False

        return True

    def check_data_catalog_exists_in_metax(self, data_catalog_id):
        if not data_catalog_id:
            log.error("Unable to check whether data catalog exists in metax since no data catalog id given. "
                      "Assuming it exists.")
            return True
        log.info("Checking if data catalog with identifier " + data_catalog_id + " already exists in Metax..")
        try:
            r = head(self.METAX_DATA_CATALOG_DETAIL_URL.format(id=data_catalog_id))
            return r.status_code == requests.codes.ok
        except Exception:
            log.error("Checking existence failed for some reason most likely in Metax data catalog API. "
                      "Assuming it exists.")
        return True

    def _do_put_request(self, url, data, api_user, api_password):
        return self._handle_request_response_with_raise(put(url,
                                                            json=data,
                                                            auth=(api_user, api_password),
                                                            verify=self.verify))

    def _do_post_request(self, url, data, api_user, api_password):
        return self._handle_request_response_with_raise(post(url,
                                                             json=data,
                                                             auth=(api_user, api_password),
                                                             verify=self.verify))

    @staticmethod
    def _handle_request_response_with_raise(response):
        log.info("Request response status code: " + str(response.status_code))
        response.raise_for_status()
        return response.text

    @staticmethod
    def get_data_catalog_id_from_file(data_catalog_json_filename):
        if not data_catalog_json_filename:
            log.error("No data catalog json filename given")
            return None

        try:
            file_path = os.path.dirname(os.path.realpath(__file__)) + '/resources/' + data_catalog_json_filename
            with open(file_path, 'r') as f:
                return json.load(f)['catalog_json'].get('identifier', None)
        except IOError:
            log.warning("No file exists in path {0} related to data catalog json filename {1}"
                        .format(file_path, data_catalog_json_filename))
            return None

    @staticmethod
    def get_data_catalog_from_file(data_catalog_json_filename):
        try:
            file_path = os.path.dirname(os.path.realpath(__file__)) + '/resources/' + data_catalog_json_filename
            with open(file_path, 'r') as f:
                return json.load(f)
        except IOError:
            log.error("No data catalog file found in path " + file_path)
            return None


def ensure_data_catalog_ok(harvest_source_name):
    if not harvest_source_name:
        log.error("No harvest source name given. Aborting.")
        return False

    data_catalog_json_filename = get_data_catalog_filename_for_harvest_source(harvest_source_name)
    dcs = DataCatalogMetaxAPIService()
    data_catalog_id = dcs.get_data_catalog_id_from_file(data_catalog_json_filename)
    if data_catalog_id:
        log.info("Data catalog id found from data catalog json file: {0}".format(data_catalog_id))
        if dcs.check_data_catalog_exists_in_metax(data_catalog_id):
            log.info("Data catalog exists in Metax, so assuming updating data catalog is OK to do..")
            if not dcs.update_data_catalog_to_metax(data_catalog_json_filename):
                log.error("Unable to update the data catalog to Metax. Aborting.")
                return False
        else:
            log.warning("Data catalog does not exist in Metax")
            created = dcs.create_data_catalog(data_catalog_json_filename)
            if not created:
                log.error("Unable to create data catalog to metax. Aborting")
                return False
    else:
        log.error("Data catalog file {0} does not contain identifier. Aborting".format(data_catalog_json_filename))
        return False

    return True


def get_data_catalog_filename_for_harvest_source(harvest_source_name):
    if harvest_source_name == 'syke':
        return 'syke_data_catalog.json'
    elif harvest_source_name == 'kielipankki':
        return 'kielipankki_data_catalog.json'
    elif harvest_source_name == 'fsd':
        return 'fsd_data_catalog.json'
    else:
        log.error("Unknown harvest source name, unable to do any data catalog related operations. Aborting")
        return False