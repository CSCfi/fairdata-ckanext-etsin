import logging
import csv
from iso639 import languages
from json import dumps, loads
from urlparse import urlparse

log = logging.getLogger(__name__)

from .data_catalog_service import DataCatalogMetaxAPIService, get_data_catalog_filename_for_harvest_source


def convert_language(language):
    """
    Convert alpha2 language (eg. 'en') to terminology language (eg. 'eng')
    """

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
    """
    Convert ISO 639-2 and 639-3 language code ('fin') to ISO 639-1 ('fi'), if possible.
    Note that not all languages are included in ISO 639-1.
    """
    try:
        part1 = languages.get(part3=language).part1
    except:
        return False

    return part1


def validate_6391(language):
    """
    Check if language code is valid ISO 639-1.
    """
    if not isinstance(language, basestring):
        return False

    try:
        part1 = languages.get(part1=language).part1
    except:
        return False

    return language == part1


def get_language_identifier(language):
    """
    Returns a URI representing the given ISO 639-3 encoded language.
    Checks first ISO 639-5 definition assuming ISO 639-3 couldn't be found in that case.
    """
    if not isinstance(language, basestring):
        language = 'und'

    try:
        languages.get(part5=language)
        # TODO: In metax language reference data iso639-5 URIs do not get validated,
        # TODO: so if the below is returned, it won't get stored to metax
        return 'http://lexvo.org/id/iso639-5/' + language
    except KeyError:
        return 'http://lexvo.org/id/iso639-3/' + language


def get_tag_lang(tag):
    """Get language of an lxml element

    :param tag: a tag of in an xml tree
    :type  tag: lxml.etree._Element
    :return a language string
    """
    xml_ns = '{http://www.w3.org/XML/1998/namespace}'
    return tag.get(xml_ns + 'lang', 'und')


def convert_to_metax_catalog_record(data_dict, context, metax_cr_id=None):
    """
    :param data_dict: contains data that has come from harvester, mapped and refined
                        and about to be sent to metax
    :param metax_cr_id: Metax catalog record identifier for the catalog record. Should be given when updating a cr.
    :return: dictionary that conforms with metax json format
    """

    metax_cr = {}
    try:
        data_catalog = DataCatalogMetaxAPIService.get_data_catalog_from_file(
            get_data_catalog_filename_for_harvest_source(context.get('harvest_source_name', '')))['catalog_json']
        data_catalog_id = data_catalog.get('identifier', None)
        if not data_catalog_id:
            raise Exception("No data catalog id can be set for metax dict")

        metax_cr['data_catalog'] = data_catalog_id
        metax_cr['metadata_provider_org'] = 'fairdata.fi'
        metax_cr['metadata_provider_user'] = 'harvest@fairdata.fi'
        if metax_cr_id:
            metax_cr['identifier'] = metax_cr_id
        if data_dict:
            metax_cr['research_dataset'] = data_dict

        # Do json dumps - loads routine to get rid of problematic character
        # encodings
        return loads(dumps(metax_cr, ensure_ascii=True))
    except KeyError as ke:
        log.error('KeyError: key not found: {0}'.format(ke.args))
    except Exception as e:
        log.error(e)


def convert_bbox_to_polygon(north, east, south, west):
    return 'POLYGON(({s} {w},{s} {e},{n} {e},{n} {w},{s} {w}))'.format(n=north, e=east, s=south, w=west)


def is_uri(string):
    """
    Guess if given string is a URI.
    """
    if string[0:4] == "urn:":
        return True
    else:
        url = urlparse(string)
        if [url.scheme, url.netloc, url.path]:
            return True
    return False


def set_existing_kata_identifier_to_other_identifier(file_path, search_pid, package_dict):
    """
    Set kata identifier to package dict (metax research dataset) other_identifier by reading a mapping file
    which contains two columns: first column contains values to search for with search_pid and the other is the value
    that should be set to package_dict.

    :param file_path:
    :param search_pid:
    :param package_dict:
    :return:
    """
    row = _find_row_from_mapping_file(file_path, search_pid)
    if row:
        set_urn_pid_to_other_identifier(row[1], package_dict)


def set_urn_pid_to_other_identifier(pid, package_dict):
    package_dict['other_identifier'] = package_dict.get('other_identifier', None) or []
    package_dict['other_identifier'].append({
        'notation': pid,
        'type': {
            'identifier': 'http://purl.org/att/es/reference_data/identifier_type/identifier_type_urn'
        }
    })


def set_existing_kata_identifier_to_preferred_identifier(file_path, search_pid, package_dict):
    """
    Set kata identifier to package dict (metax research dataset) preferred_identifier by reading a mapping file
    which contains two columns: first column contains values to search for with search_pid and the other is the value
    that should be set to package_dict.

    :param file_path:
    :param search_pid:
    :param package_dict:
    :return:
    """
    row = _find_row_from_mapping_file(file_path, search_pid)
    if row:
        package_dict['preferred_identifier'] = row[1]


def search_pid_exists_in_mapping_file(file_path, search_pid):
    """
    Verify whether a search pid exists in the mapping file which contains two columns, of which the first column
    is the column where search_pid may be found

    :param file_path:
    :param search_pid:
    :return:
    """
    if _find_row_from_mapping_file(file_path, search_pid):
        return True

    return False


def _find_row_from_mapping_file(file_path, search_pid):
    with open(file_path, 'rb') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if row[0] == search_pid:
                return row
    return None
