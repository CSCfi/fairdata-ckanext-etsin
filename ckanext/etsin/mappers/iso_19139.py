'''
Map ISO 19139 dicts to Metax values
'''

from iso639 import languages
from ..utils import get_language_identifier,\
                    convert_language_to_6391,\
                    convert_bbox_to_polygon

import logging
log = logging.getLogger(__name__)


def iso_19139_mapper(context, data_dict):
    # Start with an empty slate
    package_dict = {}

    if 'iso_values' not in data_dict:
        return {}

    iso_values = data_dict['iso_values']

    # Find out metadata language
    # Use fi/fin, if language code not given or isn't valid ISO 639-3
    try:
        lang = languages.get(part3=iso_values['metadata-language']).part3
        meta_lang = convert_language_to_6391(lang)
    except Exception:
        meta_lang = 'fi'

    # COMPULSORY FIELDS

    try:
        # Use whatever id harvest source gives us
        package_dict['preferred_identifier'] = data_dict['harvest_object'].guid
    except KeyError:
        package_dict['preferred_identifier'] = ''

    # Find title
    try:
        package_dict['title'] = [{meta_lang: iso_values['title']}]
    except KeyError:
        package_dict['title'] = [{'default': ''}]

    # OPTIONAL FIELDS

    # Dataset language
    package_dict['language'] = []
    try:
        dataset_lang = (lang for lang in iso_values['dataset-language'])
        for ds_lang in dataset_lang:
            package_dict['language'].append({'identifier': get_language_identifier(ds_lang)})
    except Exception:
        pass

    # Description
    try:
        package_dict['description'] = [{meta_lang: iso_values['abstract']}]
    except KeyError:
        pass

    # Dataset creators
    package_dict['creator'] = []
    try:
        creators = (org for org in iso_values['responsible-organisation'] if 'originator' in org['role'])
        for creator in creators:
            _set_agent_details_to_package_dict_field(package_dict, 'creator', creator, True)
    except KeyError:
        pass

    # Dataset curator
    package_dict['curator'] = []
    try:
        curators = (org for org in iso_values['responsible-organisation'] if 'pointOfContact' in org['role'])
        for curator in curators:
            _set_agent_details_to_package_dict_field(package_dict, 'curator', curator, True)
    except KeyError:
        pass

    # Use distributor as metax publisher
    try:
        for org in iso_values['responsible-organisation']:
            if 'distributor' in org['role']:
                _set_agent_details_to_package_dict_field(package_dict, 'publisher', org, False)
                break
    except KeyError:
        pass

    # If distributor was not found for metax publisher, try publisher role for metax publisher
    if 'publisher' not in package_dict:
        try:
            for org in iso_values['responsible-organisation']:
                if 'publisher' in org['role']:
                    _set_agent_details_to_package_dict_field(package_dict, 'publisher', org, False)
                    break
        except KeyError:
            pass

    # Dataset rights holder
    try:
        for org in iso_values['responsible-organisation']:
            if 'owner' in org['role']:
                _set_agent_details_to_package_dict_field(package_dict, 'rights_holder', org, False)
                break
    except KeyError:
        pass

    # When dataset was last time modified
    try:
        package_dict['modified'] = iso_values['date-updated']
    except KeyError:
        package_dict['modified'] = ''

    # Dataset freeform keywords
    package_dict['keyword'] = []
    try:
        for tag in iso_values['tags']:
            package_dict['keyword'].append(tag)
    except KeyError:
        pass

    # Spatial information, assuming a bbox value
    package_dict['spatial'] = []
    try:
        for bbox in iso_values['bbox']:
            if 'north' in bbox and 'east' in bbox and 'south' in bbox and 'west' in bbox:
                polygon = convert_bbox_to_polygon(bbox['north'], bbox['east'], bbox['south'], bbox['west'])
                package_dict['spatial'].append({'polygon': polygon})
    except KeyError:
        pass

    # Temporal extent, assumption is same index within temporal-extent-begin and -end are related
    # No dataset have had values on these.
    package_dict['temporal'] = []
    try:
        if len(iso_values['temporal-extent-begin']) == len(iso_values['temporal-extent-end']) and \
        len(iso_values['temporal-extent-begin']) > 0:
            for idx, val in enumerate(iso_values['temporal-extent-begin']):
                package_dict['temporal'].append({'start_date': val,
                                                'end_date': iso_values['temporal-extent-end'][idx]})
    except KeyError:
        pass

    # Date of formal issuance for the dataset
    try:
        package_dict['issued'] = iso_values['date-released']
    except KeyError:
        pass

    # Access rights description as a text
    if 'use-constraints' in iso_values and len(iso_values['use-constraints']):
        description = []
        for use_constraint in iso_values['use-constraints']:
            description.append({meta_lang: use_constraint})
        package_dict['access_rights'] = {'description': description}

    # Use lineage as description for provenance
    package_dict['provenance'] = []
    try:
        package_dict['provenance'].append({'description': iso_values['lineage']})
    except KeyError:
        pass

    # Last straws

    # Syke-specifically, use user role as value for creator if it does not exist
    # TODO: We need to ask SYKE what user role means!
    if not len(package_dict['creator']):
        try:
            for org in (org for org in iso_values['responsible-organisation'] if 'user' in org['role']):
                name = org['organisation-name'] or org.get('individual-name', '')
                email = org['contact-info'].get('email', '') if 'contact-info' in org else ''
                if 'creator' in package_dict and not len(package_dict['creator']):
                    package_dict['creator'].append({'name': name, 'email': email})
        except KeyError:
            pass

    return package_dict


def _set_agent_details_to_package_dict_field(package_dict, field, agent, is_array):
    try:
        name = agent['organisation-name'] or agent.get('individual-name', '')
        email = agent['contact-info'].get('email', '') if 'contact-info' in agent else ''
        if is_array:
            if field not in package_dict:
                package_dict[field] = []
            package_dict[field].append({'name': name, 'email': email})
        else:
            package_dict[field] = {'name': name, 'email': email}
    except Exception:
        raise
