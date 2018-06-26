# This file is part of the Etsin harvester service
#
# Copyright 2017-2018 Ministry of Education and Culture, Finland
#
# :author: CSC - IT Center for Science Ltd., Espoo Finland <servicedesk@csc.fi>
# :license: GNU Affero General Public License version 3

import requests
from requests import HTTPError, exceptions
import json
from pylons import config

import logging
log = logging.getLogger(__name__)

TIMEOUT = 30
METAX_BASE_URL = 'https://{0}'.format(config.get('metax.host'))
METAX_DATASETS_BASE_URL = METAX_BASE_URL + '/rest/datasets'
METAX_REFERENCE_DATA_URL = METAX_BASE_URL + '/es/reference_data/{topic}/_search'


def json_or_empty(response):
    response_json = ""
    try:
        response_json = response.json()
    except:
        pass
    return response_json


def get_catalog_record_identifier_using_preferred_identifier(metax_pref_id):
    """
    Get catalog record identifier for a record from MetaX using preferred identifier.

    :param metax_pref_id: MetaX catalog record preferred identifier
    :return: catalog record identifier
    """
    r = requests.get(METAX_DATASETS_BASE_URL + '?preferred_identifier={0}'.format(metax_pref_id),
                      headers={
              'Content-Type': 'application/json',
            },
                      auth=(config.get('metax.api_user'), config.get('metax.api_password')),
                      timeout=TIMEOUT)
    try:
        r.raise_for_status()
    except HTTPError as e:
        log.error('Failed to get dataset: \npreferred_identifier={metax_pref_id}, \nerror={error}, \njson={json}'.format(
            metax_pref_id=metax_pref_id, error=repr(e), json=json_or_empty(r)))
        log.error('Response text: %s', r.text)
        raise
    return json.loads(r.text)['identifier']


def create_catalog_record(cr_json):
    """
    Create a catalog record in MetaX.

    :param cr_json: MetaX catalog record json
    :return: catalog record identifier of the created catalog record.
    """
    r = requests.post(METAX_DATASETS_BASE_URL,
                      headers={
              'Content-Type': 'application/json',
            },
                      json=cr_json,
                      auth=(config.get('metax.api_user'), config.get('metax.api_password')),
                      timeout=TIMEOUT)
    try:
        r.raise_for_status()
    except HTTPError as e:
        log.error('Failed to create dataset: \ndataset={dataset}, \nerror={error}, \njson={json}'.format(
            dataset=cr_json, error=repr(e), json=json_or_empty(r)))
        log.error('Response text: %s', r.text)
        raise
    log.debug('Response text: %s', r.text)
    return json.loads(r.text)['identifier']


def update_catalog_record(metax_cr_id, cr_json):
    """
    Update existing catalog record in MetaX

    :param metax_cr_id: MetaX catalog record identifier
    :param cr_json: MetaX catalog record json
    """
    r = requests.put(METAX_DATASETS_BASE_URL + '/{id}'.format(id=metax_cr_id),
                     headers={
                'Content-Type': 'application/json'
            },
                     json=cr_json,
                     auth=(config.get('metax.api_user'), config.get('metax.api_password')),
                     timeout=TIMEOUT)
    try:
        r.raise_for_status()
    except HTTPError as e:
        log.error('Failed to update catalog record {id}: \ndataset={dataset}, \nerror={error}, \njson={json}'.format(
            dataset=cr_json, id=metax_cr_id, error=repr(e), json=json_or_empty(r)))
        log.error('Response text: %s', r.text)
        raise


def delete_catalog_record(metax_cr_id):
    """
    Delete a catalog record from MetaX.

    :param metax_cr_id: MetaX catalog record identifier
    """
    r = requests.delete(METAX_DATASETS_BASE_URL + '/{id}'.format(id=metax_cr_id),
                        auth=(config.get('metax.api_user'), config.get('metax.api_password')), timeout=TIMEOUT)
    try:
        r.raise_for_status()
    except HTTPError as e:
        log.error('Failed to delete catalog record {id}: \nerror={error}, \njson={json}'.format(
            id=metax_cr_id, error=repr(e), json=json_or_empty(r)))
        raise


def check_catalog_record_exists(metax_cr_id):
    """
    Ask MetaX whether the catalog record already exists in MetaX by using metax catalog record identifier.

    :param metax_cr_id: MetaX catalog record identifier
    :return: True/False
    """
    r = requests.head(METAX_DATASETS_BASE_URL + '/{id}'.format(id=metax_cr_id))
    return r.status_code == requests.codes.ok


def get_ref_data(topic, field, term, result_field):
    """ Query MetaX Elastic search API for all kinds of reference data

    :param topic: as one of listed <host>/es/reference_data?pretty eg. 'licese'
    :type topic: string
    :param field: of an entry to query, subfield with period eg.'label.fi'
    :type field: string
    :param term: to search eg. 'JaaSamoin'
    :type term: string
    :return:
    """
    query = json.dumps({
        "query": {
            "match": {
                field: term}, },
        "size": 1, })
    # response = requests.get(
    #     'https://{0}/es/reference_data/license/_search'.format(config.get('metax.host')), data=query)
    response = requests.get(METAX_REFERENCE_DATA_URL.format(topic=topic),
                            data=query)
    results = json.loads(response.text)
    try:
        result = results['hits']['hits'][0]['_source'][result_field]
        return result
    except:
        return None
