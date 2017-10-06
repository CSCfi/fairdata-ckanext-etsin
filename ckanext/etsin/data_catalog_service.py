import os
from requests import exceptions, get, put, post, delete
import json
from pylons import config
import logging
log = logging.getLogger(__name__)


class DataCatalogMetaxAPIService:

    METAX_DATA_CATALOG_API_POST_URL = 'https://metax-test.csc.fi/rest/datacatalogs'
    METAX_DATA_CATALOG_API_PUT_OR_DELETE_URL = 'https://metax-test.csc.fi/rest/datacatalogs' + "/{id}"
    METAX_DATA_CATALOG_API_EXISTS_URL = METAX_DATA_CATALOG_API_POST_URL + "/{id}/exists"

    def __init__(self):
        self.api_user = config.get('metax.api_user')
        self.api_password = config.get('metax.api_password')

    def create_data_catalog(self, data_catalog_json_file):
        if not data_catalog_json_file:
            log.error("No data catalog json file given, unable to create data catalog to metax")
            return None

        catalog = self.get_data_catalog_from_file(data_catalog_json_file)
        log.info("Creating data catalog into Metax..")
        try:
            response_text = self._do_post_request(self.METAX_DATA_CATALOG_API_POST_URL, catalog, self.api_user, self.api_password)
            data_catalog_id = json.loads(response_text)['catalog_json']['identifier']
            log.info("Data catalog created in Metax with identifier: {0}".format(data_catalog_id))
            return data_catalog_id
        except exceptions.HTTPError as e:
            log.error(e)
            log.error("Creating data catalog failed for some reason most likely in Metax data catalog API")
        return None

    def update_data_catalog(self, data_catalog_json_file, data_catalog_id):
        if not data_catalog_id or not data_catalog_json_file:
            log.error("No data catalog id or data catalog json file given for updating data catalog")
            return False

        catalog = self.get_data_catalog_from_file(data_catalog_json_file)
        log.info("Updating data catalog into Metax..")
        catalog['catalog_json']['identifier'] = data_catalog_id
        try:
            self._do_put_request(self.METAX_DATA_CATALOG_API_PUT_OR_DELETE_URL.format(id=data_catalog_id), catalog,
                                 self.api_user, self.api_password)
            log.info("Data catalog updated in Metax for identifier: {id}".format(id=data_catalog_id))
        except exceptions.HTTPError as e:
            log.error(e)
            log.error("Updating data catalog failed for some reason most likely in Metax data catalog API")
            return False

        return True

    def delete_data_catalog(self, data_catalog_id):
        if not data_catalog_id:
            log.error("No data catalog id given for deleting data catalog")
            return False

        log.info("Deleting data catalog in Metax..")
        try:
            self._do_delete_request(self.METAX_DATA_CATALOG_API_PUT_OR_DELETE_URL.format(id=data_catalog_id), self.api_user,
                                                  self.api_password)
            log.info("Data catalog deleted from Metax for identifier: {id}".format(id=data_catalog_id))
        except exceptions.HTTPError as e:
            log.error(e)
            log.error("Deleting data catalog failed for some reason most likely in Metax data catalog API")
            return False

        return True

    def check_data_catalog_exists(self, data_catalog_id):
        if not data_catalog_id:
            log.error("Unable to check whether data catalog exists in metax since no data catalog id given. "
                      "Assuming it exists.")
            return True
        log.info("Checking if data catalog with identifier " + data_catalog_id + " already exists in Metax..")
        try:
            catalog_exists = json.loads(get(self.METAX_DATA_CATALOG_API_EXISTS_URL.format(id=data_catalog_id)).text)
        except (exceptions.ConnectionError, exceptions.Timeout, exceptions.ConnectTimeout, exceptions.ReadTimeout):
            log.error("Checking existence failed for some reason most likely in Metax data catalog API. "
                      "Assuming it exists.")
            return True
        return catalog_exists

    def _do_put_request(self, url, data, api_user, api_password):
        return self._handle_request_response_with_raise(put(url, json=data, auth=(api_user, api_password)))

    def _do_post_request(self, url, data, api_user, api_password):
        return self._handle_request_response_with_raise(post(url, json=data, auth=(api_user, api_password)))

    def _do_delete_request(self, url, api_user, api_password):
        return self._handle_request_response_with_raise(delete(url, auth=(api_user, api_password)))

    @staticmethod
    def _handle_request_response_with_raise(response):
        log.info("Request response status code: " + str(response.status_code))
        response.raise_for_status()
        return response.text

    @staticmethod
    def set_data_catalog_id_to_file(data_catalog_id, harvest_source_name):
        try:
            file_path = '/opt/data/ckan/data_catalog/' + harvest_source_name
            with open(file_path, 'w') as f:
                f.write(data_catalog_id)
            log.info("Stored data catalog id {0} to {1}".format(data_catalog_id, harvest_source_name))
        except IOError:
            log.error("Something wrong with path {0}".format(file_path))
            return False

        return True

    @staticmethod
    def get_data_catalog_id_from_file(harvest_source_name):
        if not harvest_source_name:
            log.error("No harvest source name given")
            return None

        try:
            file_path = '/opt/data/ckan/data_catalog/' + harvest_source_name
            with open(file_path, 'r') as f:
                return f.readline()
        except IOError:
            log.warn("No file exists in path {0} related to harvest source {1}".format(file_path, harvest_source_name))
            return None

    @staticmethod
    def get_data_catalog_from_file(data_catalog_json_file):
        try:
            file_path = os.path.dirname(os.path.realpath(__file__)) + '/resources/' + data_catalog_json_file
            with open(file_path, 'r') as f:
                return json.load(f)
        except IOError:
            log.error("No data catalog file found in path " + file_path)
            return None


def ensure_data_catalog_ok(harvest_source_name):
    if not harvest_source_name:
        log.error("No harvest source name given. Aborting")
        return False

    if harvest_source_name == 'syke':
        data_catalog_json_file = 'syke_data_catalog.json'
    elif harvest_source_name == 'kielipankki':
        data_catalog_json_file = 'language_bank_data_catalog.json'
    else:
        log.error("Unknown harvest source name, unable to do any data catalog related operations. Aborting")
        return False

    dcs = DataCatalogMetaxAPIService()
    data_catalog_id = dcs.get_data_catalog_id_from_file(harvest_source_name)
    if data_catalog_id:
        log.info("Data catalog id found")
        if dcs.check_data_catalog_exists(data_catalog_id):
            log.info("Data catalog exists in metax, so assuming updating data catalog is OK to do..")
            if not dcs.update_data_catalog(data_catalog_json_file, data_catalog_id):
                log.error("Unable to update the data catalog to metax. Aborting.")
                return False
        else:
            log.warn("Data catalog cannot be found from metax even though we have a data catalog id. Trying to "
                     "recreate data catalog and overwrite the existing data catalog id")
            data_catalog_id = dcs.create_data_catalog(data_catalog_json_file)
            if data_catalog_id:
                if not dcs.set_data_catalog_id_to_file(data_catalog_id, harvest_source_name):
                    log.error("Unable to store data catalog id to file. Aborting")
                    log.error("Go and delete the data catalog from metax manually since it was created there"
                              "but its id cannot be stored to a file")
                    return False
            else:
                log.error("Unable to create data catalog to metax. Aborting")
                return False

    else:
        log.info("Data catalog id not found, so assuming create data catalog is OK to do..")
        data_catalog_id = dcs.create_data_catalog(data_catalog_json_file)
        if data_catalog_id:
            if not dcs.set_data_catalog_id_to_file(data_catalog_id, harvest_source_name):
                log.error("Unable to store data catalog id to file. Aborting")
                log.error("Go and delete the data catalog from metax manually since it was created there"
                          "but its id cannot be stored to a file")
                return False
        else:
            log.error("Unable to create data catalog to metax. Aborting")
            return False

    return True
