'''
Map ISO 19139 dicts to Metax values
'''

from iso639 import languages

# For development use
import logging
log = logging.getLogger(__name__)

# Overwrites ckanext-spatial's get_package_dict
def iso_19139_mapper(self, context, data_dict):

    # Start with an empty slate
    package_dict = {}

    # METAX OBLIGATORY FIELDS
    # Don't mind missing values. We'll let Metax handle them.

    # Obligatory in API but not in Metax data model
    try:
        # Use whatever id harvest source gives us
        package_dict['preferred_identifier'] = data_dict['iso_values']['guid']
    except KeyError:
        package_dict['preferred_identifier'] = ''

    try:
        # Harvest source only ever has one title, so no need to bother with language codes.
        package_dict['title'] = [{'default': data_dict['iso_values']['title']}]
    except KeyError:
        package_dict['title'] = [{'default': ''}]

    # Find creators, if any
    package_dict['creator'] = []
    try:
        creators = (org for org in data_dict['iso_values']['responsible-organisation'] if 'author' in org['role'])
        for org in creators:
            package_dict['creator'].append({'name': org['organisation-name']})
    except KeyError:
        pass

    # Find curators, if any
    package_dict['curator'] = []
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

    # METAX OPTIONAL FIELDS
    
    # ['tags']['name'] to keywords
    # ['abstract'] to description (localized text)
    # ['temporal-extent-begin'] and ['temporal-extent-end'] to temporal (keys start_date and end_date)
    # copy package_dict['curator'] to owner
    # ['responsible-organization']['role'='distributor'] to distributor
    # ['bbox'] to location (unclear how to turn bbox into point coordinates)
    # ['metadata-date'] to issued?
    # ['contact-email'] to ['curator']['email'] and ['owner']['email']

    return package_dict


def _get_language_identifier(lang):
    if not isinstance(lang, basestring):
        lang = 'und'

    return 'http://www.lexvo.org/id/iso639-3/' + lang
