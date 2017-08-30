import os
import requests
import json
import logging
import requests.exceptions
log = logging.getLogger(__name__)


def get_data_catalog_id(harvest_source_config):
    if harvest_source_config and harvest_source_config.get('data_catalog_json_file', False):
        data_catalog_json_file = harvest_source_config.get('data_catalog_json_file')
        catalog_service = DataCatalogMetaxAPIService()
        return catalog_service.create_or_update_data_catalogs(True, data_catalog_json_file)
    return None


class DataCatalogMetaxAPIService:
    '''
        This class can be used either from command line or CKAN extension.
        In CKAN, import this class and instantiate, then call
        create_or_update_data_catalogs method by giving data catalog
        json file path and boolean for whether data catalog should be
        updated if it exists.
    '''

    METAX_DATA_CATALOG_API_POST_URL = 'https://metax-test.csc.fi/rest/datacatalogs'
    METAX_DATA_CATALOG_API_PUT_URL = 'https://metax-test.csc.fi/rest/datacatalogs' + "/{id}"
    METAX_DATA_CATALOG_API_EXISTS_URL = METAX_DATA_CATALOG_API_POST_URL + "/{id}/exists"

    def create_or_update_data_catalogs(self, update_if_exists, data_catalog_json_file):
        '''
        Return data catalog identifier
        '''

        try:
            file_path = os.path.dirname(os.path.realpath(__file__)) + '/resources/' + data_catalog_json_file
            catalog = self._get_data_catalogs_from_file(file_path)
        except IOError:
            log.error("No data catalog file found in path " + file_path)
            raise

        c_identifier = catalog['catalog_json']['identifier']
        log.info("Checking if data catalog with identifier " + c_identifier + " already exists in Metax..")
        try:
            catalog_exists = json.loads(requests.get(self.METAX_DATA_CATALOG_API_EXISTS_URL.format(id=c_identifier)).text)
        except (ConnectionError, Timeout, ConnectTimeout, ReadTimeout):
            log.error("Checking existence failed for some reason most likely in Metax data catalog API")
            raise

        if catalog_exists:
            log.info("Data catalog already exists in Metax")
        else:
            log.info("Data catalog does not exist in Metax")

        if update_if_exists and catalog_exists:
            log.info("Updating data catalog in Metax..")
            try:
                self._do_put_request(self.METAX_DATA_CATALOG_API_PUT_URL.format(id=c_identifier), catalog)
                log.info("Data catalog updated in Metax")
            except requests.exceptions.HTTPError:
                log.error("Updating data catalog failed for some reason most likely in Metax data catalog API")
                raise
        elif not catalog_exists:
            log.info("Creating data catalog in Metax..")
            try:
                response_text = self._do_post_request(self.METAX_DATA_CATALOG_API_POST_URL, catalog)
                log.info("Data catalog created in Metax")
                log.info(response_text)
            except requests.exceptions.HTTPError:
                log.error("Creating data catalog failed for some reason most likely in Metax data catalog API")
                raise
        elif not update_if_exists and catalog_exists:
            log.info("Skipping data catalog update in Metax..")

        return c_identifier

    def _do_put_request(self, url, data):
        return self._handle_request_response_with_raise(requests.put(url, json=data))

    def _do_post_request(self, url, data):
        return self._handle_request_response_with_raise(requests.post(url, json=data))

    def _handle_request_response_with_raise(self, response):
        log.debug("Request response status code: " + str(response.status_code))
        response.raise_for_status()
        return response.text

    def _get_data_catalogs_from_file(self, data_catalog_file_path):
        with open(data_catalog_file_path, 'r') as f:
            return json.load(f)

def main():
    import sys
    import pprint
    UPDATE_IF_EXISTS = 'update_if_exists'
    DATA_CATALOG_JSON_FILE_PATH = 'data_catalog_json_file_path'
    run_args = dict([arg.split('=') for arg in sys.argv[1:]])

    if not UPDATE_IF_EXISTS in run_args or not DATA_CATALOG_JSON_FILE_PATH in run_args:
        pprint.pprint("Run by: 'python <filename>.py update_if_exists=? data_catalog_json_file_path=%', where ? is either True or False and % path to data catalog json file")
        sys.exit(1)

    if run_args[UPDATE_IF_EXISTS] != 'True' and run_args[UPDATE_IF_EXISTS] != 'False':
        pprint.pprint("Invalid update_if_exists value")
        sys.exit(1)

    update_if_exists = True if run_args[UPDATE_IF_EXISTS] == 'True' else False
    input_file_path = run_args[DATA_CATALOG_JSON_FILE_PATH]
    catalog_service = DataCatalogMetaxAPIService()
    catalog_service.create_or_update_data_catalogs(update_if_exists, input_file_path)

if __name__ == '__main__':
    # calling main function
    main()
