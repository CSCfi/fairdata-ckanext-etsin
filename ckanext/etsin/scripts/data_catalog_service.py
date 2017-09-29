import os
import sys
from requests import exceptions, get, put, post, delete
import json
import pprint


class DataCatalogMetaxAPIService:

    METAX_DATA_CATALOG_API_POST_URL = 'https://metax-test.csc.fi/rest/datacatalogs'
    METAX_DATA_CATALOG_API_PUT_OR_DELETE_URL = 'https://metax-test.csc.fi/rest/datacatalogs' + "/{id}"
    METAX_DATA_CATALOG_API_EXISTS_URL = METAX_DATA_CATALOG_API_POST_URL + "/{id}/exists"

    def __init__(self, api_user, api_password):
        self.api_user = api_user
        self.api_password = api_password

    def create_data_catalog(self, data_catalog_json_file):
        catalog = get_data_catalog_from_file(data_catalog_json_file)

        pprint.pprint("Creating data catalog in Metax..")
        try:
            response_text = self._do_post_request(self.METAX_DATA_CATALOG_API_POST_URL, catalog, self.api_user, self.api_password)
            pprint.pprint("Data catalog created in Metax with identifier: {0}".format(json.loads(response_text)['catalog_json']['identifier']))
        except exceptions.HTTPError:
            pprint.pprint("Creating data catalog failed for some reason most likely in Metax data catalog API")
            sys.exit(1)

    def update_data_catalog(self, data_catalog_json_file, data_catalog_id):
        catalog = get_data_catalog_from_file(data_catalog_json_file)
        if not data_catalog_id:
            pprint.pprint("No data catalog id given for updating data catalog {file}".format(data_catalog_json_file))
            sys.exit(1)

            pprint.pprint("Checking if data catalog with identifier " + data_catalog_id + " already exists in Metax..")
        try:
            catalog_exists = json.loads(get(self.METAX_DATA_CATALOG_API_EXISTS_URL.format(id=data_catalog_id)).text)
        except (exceptions.ConnectionError, exceptions.Timeout, exceptions.ConnectTimeout, exceptions.ReadTimeout):
            pprint.pprint("Checking existence failed for some reason most likely in Metax data catalog API")
            sys.exit(1)

        if catalog_exists:
            pprint.pprint("Data catalog exists in Metax!")
        else:
            pprint.pprint("Data catalog does not exist in Metax, make sure it exists there before trying to update")
            sys.exit(1)

        if catalog_exists:
            pprint.pprint("Updating data catalog in Metax..")
            catalog['catalog_json']['identifier'] = data_catalog_id
            try:
                self._do_put_request(self.METAX_DATA_CATALOG_API_PUT_OR_DELETE_URL.format(id=data_catalog_id), catalog, self.api_user, self.api_password)
                pprint.pprint("Data catalog updated in Metax for identifier: {id}".format(id=data_catalog_id))
            except exceptions.HTTPError:
                pprint.pprint("Updating data catalog failed for some reason most likely in Metax data catalog API")
                sys.exit(1)

    def delete_data_catalog(self, data_catalog_id):
        if not data_catalog_id:
            pprint.pprint("No data catalog id given for deleting data catalog")
            sys.exit(1)

        pprint.pprint("Deleting data catalog in Metax..")
        try:
            self._do_delete_request(self.METAX_DATA_CATALOG_API_PUT_OR_DELETE_URL.format(id=data_catalog_id), self.api_user,
                                                  self.api_password)
            pprint.pprint("Data catalog deleted from Metax for identifier: {id}".format(id=data_catalog_id))
        except exceptions.HTTPError:
            pprint.pprint("Deleting data catalog failed for some reason most likely in Metax data catalog API")
            sys.exit(1)

    def _do_put_request(self, url, data, api_user, api_password):
        return self._handle_request_response_with_raise(put(url, json=data, auth=(api_user, api_password)))

    def _do_post_request(self, url, data, api_user, api_password):
        return self._handle_request_response_with_raise(post(url, json=data, auth=(api_user, api_password)))

    def _do_delete_request(self, url, api_user, api_password):
        return self._handle_request_response_with_raise(delete(url, auth=(api_user, api_password)))

    def _handle_request_response_with_raise(self, response):
        pprint.pprint("Request response status code: " + str(response.status_code))
        response.raise_for_status()
        return response.text


def get_data_catalog_from_file(data_catalog_json_file):
    try:
        file_path = os.path.dirname(os.path.realpath(__file__)) + '/resources/' + data_catalog_json_file
        with open(file_path, 'r') as f:
            return json.load(f)
    except IOError:
        pprint.pprint("No data catalog file found in path " + file_path)
        raise


def main():

    API_USER = 'api_user'
    API_PASSWORD = 'api_password'
    DATA_CATALOG_ID = 'data_catalog_id'
    DATA_CATALOG_JSON_FILE_NAME = 'data_catalog_json_file_name'
    run_args = dict([arg.split('=') for arg in sys.argv[1:]])
    data_catalog_id = None
    data_catalog_json_file_name = None

    if not API_USER in run_args or API_PASSWORD not in run_args:
        pprint.pprint("Run by: 'python data_catalog_service.py data_catalog_json_file_name=X data_catalog_id=Y api_user=Z api_password=W', api_user and api_password are compulsory. X is the name of the data catalog json file located in resources folder and Y is the data catalog identifier. Z and W are credentials for using metax API. Three use cases: 1) If both data_catalog_json_file_name and data_catalog_id are given, an update operation is assumed. 2) If only data_catalog_json_file_name is given, a create operation is assumed. 3) If only data_catalog_id is given, a delete operation is assumed.")
        sys.exit(1)

    api_user = run_args[API_USER]
    api_password = run_args[API_PASSWORD]

    if DATA_CATALOG_ID in run_args:
        data_catalog_id = run_args[DATA_CATALOG_ID]

    if DATA_CATALOG_JSON_FILE_NAME in run_args:
        data_catalog_json_file_name = run_args[DATA_CATALOG_JSON_FILE_NAME]

    catalog_service = DataCatalogMetaxAPIService(api_user, api_password)
    if data_catalog_json_file_name and data_catalog_id:
        catalog_service.update_data_catalog(data_catalog_json_file_name, data_catalog_id)
    elif data_catalog_json_file_name:
        catalog_service.create_data_catalog(data_catalog_json_file_name)
    elif data_catalog_id:
        catalog_service.delete_data_catalog(data_catalog_id)

if __name__ == '__main__':
    # calling main function
    main()
