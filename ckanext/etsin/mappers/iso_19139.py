'''
Map ISO 19139 dicts to Metax values
'''

from iso639 import languages
from ..utils import get_language_identifier, convert_language_to_6391

import logging
log = logging.getLogger(__name__)


# Overwrites ckanext-spatial's get_package_dict
def iso_19139_mapper(context, data_dict):
    # Start with an empty slate
    package_dict = {}

    # METAX OBLIGATORY FIELDS
    # Don't mind missing values. We'll let Metax handle them.

    # Obligatory in API but not in Metax data model
    try:
        # Use whatever id harvest source gives us
        package_dict['preferred_identifier'] = data_dict['harvest_object'].guid
    except KeyError:
        package_dict['preferred_identifier'] = ''

    # Use 'undefined' if language code not given or isn't valid ISO 639-3
    try:
        lang = languages.get(part3=data_dict['iso_values'][
                             'metadata-language']).part3
    except:
        lang = 'und'
    package_dict['language'] = [{'identifier': get_language_identifier(lang)}]

    # Find title
    try:
        package_dict['title'] = [{convert_language_to_6391(lang): data_dict['iso_values']['title']}]
    except KeyError:
        package_dict['title'] = [{'default': ''}]

    try:
        package_dict['modified'] = data_dict['iso_values']['date-updated']
    except KeyError:
        package_dict['modified'] = ''

    # Find creators, if any
    package_dict['creator'] = []
    # package_dict['creator'] = [{'name': 'TEST'}]
    try:
        creators = (org for org in data_dict['iso_values'][
                    'responsible-organisation'] if 'author' in org['role'])
        for org in creators:
            package_dict['creator'].append({'name': org['organisation-name']})
    except KeyError:
        pass

    # Find curators, if any
    package_dict['curator'] = []
    # package_dict['curator'] = [{'name': 'TEST'}]
    try:
        curators = (org for org in data_dict['iso_values'][
                    'responsible-organisation'] if 'owner' in org['role'])
        for org in curators:
            package_dict['curator'].append({'name': org['organisation-name']})
    except KeyError:
        pass

    # METAX OPTIONAL FIELDS

    try:
        package_dict['description'] = [
            {convert_language_to_6391(lang): data_dict['iso_values']['abstract']}]
    except KeyError:
        pass

    # ['tags']['name'] to keywords
    # ['abstract'] to description (localized text)
    # ['temporal-extent-begin'] and ['temporal-extent-end'] to temporal (keys start_date and end_date)
    # copy package_dict['curator'] to owner
    # ['responsible-organization']['role'='distributor'] to distributor
    # ['bbox'] to location (unclear how to turn bbox into point coordinates)
    # ['metadata-date'] to issued?
    # ['contact-email'] to ['curator']['email'] and ['owner']['email']

    return package_dict
