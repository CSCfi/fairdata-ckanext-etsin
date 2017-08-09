import requests
import json
import pprint

class DatasetCatalogMetaxAPIService:
    '''
        This class can be used either from command line or CKAN extension.
        In CKAN, import this class and instantiate, then call
        create_or_update_dataset_catalogs method by giving data catalog
        json file path and boolean for whether data catalog should be
        updated if it exists. Use at the beginning of harvester?
    '''

    METAX_DATASET_CATALOG_API_POST_URL = 'https://metax-test.csc.fi/rest/datasetcatalogs'
    METAX_DATASET_CATALOG_API_PUT_URL = 'https://metax-test.csc.fi/rest/datasetcatalogs' + "/{id}"
    METAX_DATASET_CATALOG_API_EXISTS_URL = METAX_DATASET_CATALOG_API_POST_URL + "/{id}/exists"

    def create_or_update_dataset_catalogs(self, update_if_exists, input_file_path):
        '''
        Return identifier for placing into metax dataset
        '''

        try:
            catalog = self._get_data_catalogs_from_file(input_file_path)
        except IOError:
            pprint.pprint("No file found in path " + input_file_path)
            return

        c_identifier = catalog['catalog_json']['identifier']
        pprint.pprint("Checking if dataset catalog with identifier " + c_identifier + " already exists in Metax..")
        try:
            dataset_exists = json.loads(self._do_get_request(self.METAX_DATASET_CATALOG_API_EXISTS_URL.format(id=c_identifier)))
        except requests.exceptions.HTTPError:
            pprint.pprint("Checking failed for some reason most likely in Metax dataset catalog API")
            return

        if dataset_exists:
            pprint.pprint("Dataset catalog already exists")
        else:
            pprint.pprint("Dataset catalog does not exist")

        if update_if_exists and dataset_exists:
            pprint.pprint("Updating dataset catalog..")
            try:
                response_text = self._do_put_request(self.METAX_DATASET_CATALOG_API_PUT_URL.format(id=c_identifier), catalog)
                pprint.pprint("Dataset catalog updated")
            except requests.exceptions.HTTPError:
                pprint.pprint("Updating dataset catalog failed for some reason most likely in Metax dataset catalog API")
                return
        elif not dataset_exists:
            pprint.pprint("Creating dataset catalog..")
            try:
                response_text = self._do_post_request(self.METAX_DATASET_CATALOG_API_POST_URL, catalog)
                pprint.pprint("Dataset catalog created")
                pprint.pprint(response_text)
            except requests.exceptions.HTTPError:
                pprint.pprint("Creating dataset catalog failed for some reason most likely in Metax dataset catalog API")
                return
        elif not update_if_exists and dataset_exists:
            pprint.pprint("Skipping dataset catalog..")

        return c_identifier

    def _do_put_request(self, url, data):
        return self._handle_request_response(requests.put(url, json=data))

    def _do_get_request(self, url):
        return self._handle_request_response(requests.get(url))

    def _do_post_request(self, url, data):
        return self._handle_request_response(requests.post(url, json=data))

    def _handle_request_response(self, response):
        pprint.pprint("Request response status code: " + str(response.status_code))
        response.raise_for_status()
        return response.text

    def _get_data_catalogs_from_file(self, input_file_path):
        with open(input_file_path, 'r') as f:
            return json.load(f)

def main():
    import sys
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
    catalog_service = DatasetCatalogMetaxAPIService()
    catalog_service.create_or_update_dataset_catalogs(update_if_exists, input_file_path)

if __name__ == '__main__':
    # calling main function
    main()
