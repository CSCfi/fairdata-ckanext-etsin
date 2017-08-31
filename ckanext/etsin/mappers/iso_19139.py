'''
Map ISO 19139 dicts to Metax values
'''

from iso639 import languages

import logging
log = logging.getLogger(__name__)


# Overwrites ckanext-spatial's get_package_dict
def iso_19139_mapper(context, data_dict):
    # Start with an empty slate
    package_dict = {}

    # Metax obligatory fields
    # Don't mind missing values. We'll let Metax handle them.

    # Obligatory in API but not in Metax data model
    try:
        # Use whatever id harvest source gives us
        package_dict['preferred_identifier'] = data_dict['harvest_object'].guid
    except KeyError:
        package_dict['preferred_identifier'] = ''

    try:
        package_dict['modified'] = data_dict['iso_values']['date-updated']
    except KeyError:
        package_dict['modified'] = ''

    try:
        package_dict['description'] = [{'fi': data_dict.get('iso_values').get('abstract')}]
    except KeyError:
        package_dict['description'] = ''

    try:
        # Harvest source only ever has one title, so no need to bother with language codes.
        package_dict['title'] = [{'default': data_dict['iso_values']['title']}]
    except KeyError:
        package_dict['title'] = [{'default': ''}]

    # Find creators, if any
    # package_dict['creator'] = []
    package_dict['creator'] = [{'name': 'TEST'}]
    try:
        creators = (org for org in data_dict['iso_values']['responsible-organisation'] if 'author' in org['role'])
        for org in creators:
            package_dict['creator'].append({'name': org['organisation-name']})
    except KeyError:
        pass

    # Find curators, if any
    # package_dict['curator'] = []
    package_dict['curator'] = [{'name': 'TEST'}]
    try:
        curators = (org for org in data_dict['iso_values']['responsible-organisation'] if 'owner' in org['role'])
        for org in curators:
            package_dict['curator'].append({'name': org['organisation-name']})
    except KeyError:
        pass

    # Use 'undefined' if language code not given or isn't valid ISO 639-3
    try:
        lang = languages.get(part3=data_dict['iso_values']['metadata-language']).part3
    except:
        lang = 'und'
    package_dict['language'] = [{'identifier': _get_language_identifier(lang)}]

    return package_dict


def _get_language_identifier(lang):
    if not isinstance(lang, basestring):
        lang = 'und'

    return 'http://lexvo.org/id/iso639-3/' + lang
