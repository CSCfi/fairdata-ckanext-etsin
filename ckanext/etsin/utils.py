# This file is part of the Etsin harvester service
#
# Copyright 2017-2018 Ministry of Education and Culture, Finland
#
# :author: CSC - IT Center for Science Ltd., Espoo Finland <servicedesk@csc.fi>
# :license: GNU Affero General Public License version 3

import logging
import csv
from iso639 import languages
from dateutil import parser
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
    return 'POLYGON(({w} {s},{w} {n},{e} {n},{e} {s},{w} {s}))'.format(n=north, e=east, s=south, w=west)


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


def str_to_bool(s):
    if s == 'True' or s == 'true':
        return True
    elif s == 'False' or s == 'false':
        return False
    else:
        log.error("Unable to convert {0} to Python boolean. Returning False.".format(s))
        return False


def get_string_as_valid_date_string(str_val, month_day_to_add_if_not_present=None):
    if str_val is None or not str_val:
        raise Exception("get_string_as_valid_date_string method must have str_val input that is not empty")

    if month_day_to_add_if_not_present is not None:
        if len(month_day_to_add_if_not_present) != 5 or '-' not in month_day_to_add_if_not_present:
            log.debug(
                "Unable to understand month_day_to_add_if_not_present: {0}".format(month_day_to_add_if_not_present))
        exit(1)

    # For cases e.g. 2010-01-1, 2010-1-01, 2010-1, 2010-1-1
    # Above example would be transformed into 2010-01-01
    if 4 < len(str_val) < 10:
        date_splitted = str_val.split('-', 3)
        if len(date_splitted) < 3:
            log.debug("Unable to parse {0}".format(str_val))
            return None
        if len(date_splitted[0]) != 4:
            log.debug("Unable to parse year in {0}".format(date_splitted[0]))
            return None

        output = date_splitted[0]
        if len(date_splitted[1]) == 1:
            output += '0' + date_splitted[1]
        else:
            output += date_splitted[1]
        if len(date_splitted[2]) == 1:
            output += '0' + date_splitted[2]
        else:
            output += date_splitted[2]
        str_val = output

    try:
        str_as_datetime = parser.isoparse(str_val)
    except:
        log.debug('Unable to parse {0}.'.format(str_val))
        return None

    if 'T' in str_val or len(str_val) > 10:
        # Cannot have time
        log.debug(
            'Unable to parse {0} as date value accepted by Metax. Contains time, in which case it cannot be reliably '
            'converted to date.'.format(str_val))
        return None

    if len(str_val) == 4:
        try:
            int(str_val)
        except ValueError:
            log.debug("String {0} is not integer".format(str_val))
            return None

        if month_day_to_add_if_not_present is None:
            log.debug('Unable to convert {0} to datetime value accepted by Metax, since contains only year info. '
                      'Must specify MM-DD.'.format(str_val))
            return None
        else:
            str_as_datetime = parser.isoparse(str_val + '-' + month_day_to_add_if_not_present)

    # datetime strftime is not able to parse years before 1900, hence the use of isoformat
    return str_as_datetime.isoformat().split('T')[0]


def get_string_as_valid_datetime_string(str_val, month_day_to_add_if_not_present=None, time_to_add_if_not_present=None):
    if str_val is None or not str_val:
        raise Exception("get_string_as_valid_datetime_string method must have str_val input that is not empty")

    if time_to_add_if_not_present is not None:
        if '+' in time_to_add_if_not_present or '-' in time_to_add_if_not_present or 'Z' in time_to_add_if_not_present:
            log.debug("No timezone info allowed in time_to_add_if_not_present parameter: {0}".format(
                time_to_add_if_not_present))
            raise Exception
        if len(time_to_add_if_not_present) != 8:
            log.debug(
                "Unable to understand time_to_add_if_not_present paremeter: {0}".format(time_to_add_if_not_present))
            raise Exception
    if month_day_to_add_if_not_present is not None:
        if len(month_day_to_add_if_not_present) != 5 or '-' not in month_day_to_add_if_not_present:
            log.debug(
                "Unable to understand month_day_to_add_if_not_present: {0}".format(month_day_to_add_if_not_present))
            raise Exception

    # For cases e.g. 2010-01-1, 2010-1-01, 2010-1, 2010-1-1
    # Above example would be transformed into 2010-01-01
    if 4 < len(str_val) < 10:
        date_splitted = str_val.split('-', 3)
        if len(date_splitted) < 3:
            log.debug("Unable to parse {0}".format(str_val))
            return None
        if len(date_splitted[0]) != 4:
            log.debug("Unable to parse year in {0}".format(date_splitted[0]))
            return None

        output = date_splitted[0]
        if len(date_splitted[1]) == 1:
            output += '0' + date_splitted[1]
        else:
            output += date_splitted[1]
        if len(date_splitted[2]) == 1:
            output += '0' + date_splitted[2]
        else:
            output += date_splitted[2]
        str_val = output

    try:
        str_as_datetime = parser.isoparse(str_val)
    except:
        log.debug('Unable to parse {0}.'.format(str_val))
        return None

    # If only year is given
    if len(str_val) == 4:
        try:
            int(str_val)
        except ValueError:
            log.debug("String {0} is not integer".format(str_val))
            return None

        if month_day_to_add_if_not_present is None:
            log.debug(
                'Unable to convert {0} to datetime value accepted by Metax, since contains only year info. '
                'Must specify MM-DD. Preferably define also time using time_to_add_if_not_present.'.format(str_val))
            return None
        else:
            str_as_datetime = parser.isoparse(str_val + '-' + month_day_to_add_if_not_present)

    if 'T' not in str_val:
        # datetime strftime is not able to parse years before 1900, hence the use of isoformat
        date_as_valid_str = str_as_datetime.isoformat().split('T')[0]
        if time_to_add_if_not_present is None:
            return date_as_valid_str + 'T00:00:00-00:00'
        else:
            return date_as_valid_str + 'T' + time_to_add_if_not_present + '-00:00'
    else:
        str_as_iso_format = str_as_datetime.isoformat()
        if '+' not in str_as_iso_format and 'Z' not in str_as_iso_format and '-' not in str_as_iso_format.split('T')[1]:
            str_as_iso_format = str_as_iso_format + '-00:00'
        return str_as_iso_format
