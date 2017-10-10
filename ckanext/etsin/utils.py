import logging
import csv
import requests
from iso639 import languages
from json import dumps, loads
from urlparse import urlparse

log = logging.getLogger(__name__)

from data_catalog_service import DataCatalogMetaxAPIService

def convert_language(language):
    '''
    Convert alpha2 language (eg. 'en') to terminology language (eg. 'eng')
    '''

    if not language:
        return "und"

    # Test if already correct form.
    if len(language) == 3 and language[0].islower():
        return language

    try:
        lang_object = languages.get(part1=language)
        return lang_object.terminology
    except KeyError as ke:
        try:
            lang_object = languages.get(part2b=language)
            return lang_object.terminology
        except KeyError as ke:
            log.error('KeyError: key not found: {0}'.format(ke.args))
            return ''


def convert_language_to_6391(language):
    '''
    Convert ISO 639-2 and 639-3 language code ('fin') to ISO 639-1 ('fi'), if possible.
    Note that not all languages are included in ISO 639-1.
    '''
    try:
        part1 = languages.get(part3=language).part1
    except:
        return False

    return part1


def validate_6391(language):
    '''
    Check if language code is valid ISO 639-1.
    '''
    if not isinstance(language, basestring):
        return False

    try:
        part1 = languages.get(part1=language).part1
    except:
        return False

    return language == part1


def get_language_identifier(language):
    '''
    Returns a URI representing the given ISO 639-3 encoded language.
    Checks first ISO 639-5 definition assuming ISO 639-3 couldn't be found in that case.
    '''
    if not isinstance(language, basestring):
        language = 'und'

    try:
        languages.get(part5=language)
        # TODO: In metax language reference data iso639-5 URIs do not get validated,
        # TODO: so if the below is returned, it won't get stored to metax
        return 'http://lexvo.org/id/iso639-5/' + language
    except KeyError:
        return 'http://lexvo.org/id/iso639-3/' + language


def convert_to_metax_dict(data_dict, context, metax_id=None):
    '''
    :param data_dict: contains data that has come from harvester, mapped and refined
                        and about to be sent to metax
    :return: data_dict that conforms with metax json format
    '''

    if metax_id:
        data_dict['urn_identifier'] = metax_id
    try:
        data_catalog_id = DataCatalogMetaxAPIService.get_data_catalog_id_from_file(
            context.get('harvest_source_name', ''))
        if not data_catalog_id:
            raise Exception("No data catalog id can be set for metax dict")
        # Do json dumps - loads routine to get rid of problematic character
        # encodings
        return loads(dumps({'research_dataset': data_dict, 'data_catalog': data_catalog_id}, ensure_ascii=True))
    except KeyError as ke:
        log.error('KeyError: key not found: {0}'.format(ke.args))
    except Exception as e:
        log.error(e)


def convert_bbox_to_polygon(north, east, south, west):
    return 'POLYGON(({s} {w},{s} {e},{n} {e},{n} {w},{s} {w}))'.format(n=north, e=east, s=south, w=west)


def is_uri(string):
    '''
    Guess if given string is a URI.
    '''
    if string[0:4] == "urn:":
        return True
    else:
        url = urlparse(string)
        if [url.scheme, url.netloc, url.path]:
            return True
    return False


# TODO This is probably not the only thing we'll be querying, so we should
# refactor this to fetch all kinds of reference data instead of just
# licenses
def get_rights_identifier(rights_URI):
    query = dumps({
        "query": {
            "match": {
                "uri": rights_URI
            },
        },
        "size": 1,
    })
    response = requests.get(
        "https://metax-test.csc.fi/es/reference_data/license/_search", data=query)
    results = loads(response.text)
    try:
        identifier = results['hits']['hits'][0]['_source']['id']
        return identifier
    except:
        return None

    return None


def set_existing_kata_identifier_to_other_identifier(file_path, search_pid, package_dict):
    package_dict['other_identifier'] = []
    with open(file_path, 'rb') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if row[0] == search_pid:
                package_dict['other_identifier'].append({
                    'notation': row[1],
                    'type': {
                         'identifier': 'http://purl.org/att/es/reference_data/identifier_type/identifier_type_urn'
                    }
                })
