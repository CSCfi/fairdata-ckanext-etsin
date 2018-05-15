"""
Map ISO 19139 dicts to Metax values
"""

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

    # Set guid to context for refiner use
    context['guid'] = data_dict['harvest_object'].guid

    # Find out metadata language
    # Use und, if language code not given or isn't valid ISO 639-3
    try:
        lang = languages.get(part3=iso_values['metadata-language']).part3
        meta_lang = convert_language_to_6391(lang)
    except Exception:
        meta_lang = 'und'

    # Ensure meta_lang exists
    if not meta_lang:
        meta_lang = 'und'

    # Find title
    try:
        package_dict['title'] = {meta_lang: iso_values['title']}
    except KeyError:
        package_dict['title'] = {'und': ''}

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

    # Field of Science
    try:
        if len(iso_values['topic-category']):
            topic_cat = iso_values['topic-category'][0]
            if topic_cat == 'environment':
                package_dict['field_of_science'] = [{'identifier': 'ta1172'}]
            elif topic_cat == 'planningCadastre':
                package_dict['field_of_science'] = [{'identifier': 'ta212'}]
            elif topic_cat == 'transportation':
                package_dict['field_of_science'] = [{'identifier': 'ta212'}]
            elif topic_cat == 'economy':
                package_dict['field_of_science'] = [{'identifier': 'ta5'}]
            elif topic_cat == 'biota':
                package_dict['field_of_science'] = [{'identifier': 'ta1181'}, {'identifier': 'ta1183'}]
            elif topic_cat == 'utilitiesCommunication':
                package_dict['field_of_science'] = [{'identifier': 'ta218'}, {'identifier': 'ta213'}]
            elif topic_cat == 'geoscientificInformation':
                package_dict['field_of_science'] = [{'identifier': 'ta1171'}]
            elif topic_cat == 'climatologyMeteorologyAtmosphere':
                package_dict['field_of_science'] = [{'identifier': 'ta1171'}]
            elif topic_cat == 'farming':
                package_dict['field_of_science'] = [{'identifier': 'ta412'}, {'identifier': 'ta4111'}]
            elif topic_cat == 'inlandWaters':
                package_dict['field_of_science'] = [{'identifier': 'ta1171'}]
            elif topic_cat == 'health':
                package_dict['field_of_science'] = [{'identifier': 'ta316'}, {'identifier': 'ta3142'}]
            elif topic_cat == 'society':
                package_dict['field_of_science'] = [{'identifier': 'ta8'}]
            else:
                package_dict['field_of_science'] = []
    except KeyError:
        package_dict['field_of_science'] = []

    # Dataset creators
    # TODO
    package_dict['creator'] = []
    try:
        creators = (org for org in iso_values['responsible-organisation'] if 'originator' in org['role'])
        for creator in creators:
            _set_agent_details_to_package_dict_field(package_dict, 'creator', creator, True, meta_lang)
    except KeyError:
        pass

    # Dataset curator
    # TODO
    package_dict['curator'] = []

    if not len(package_dict['curator']):
        try:
            curators = (org for org in iso_values['responsible-organisation'] if 'pointOfContact' in org['role'])
            for curator in curators:
                _set_agent_details_to_package_dict_field(package_dict, 'curator', curator, True, meta_lang)
        except KeyError:
            pass

    # Use distributor as metax publisher
    # TODO
    try:
        for org in iso_values['responsible-organisation']:
            if 'distributor' in org['role']:
                _set_agent_details_to_package_dict_field(package_dict, 'publisher', org, False, meta_lang)
                break
    except KeyError:
        pass

    # If distributor was not found for metax publisher, try publisher role for metax publisher
    # TODO
    if 'publisher' not in package_dict:
        try:
            for org in iso_values['responsible-organisation']:
                if 'publisher' in org['role']:
                    _set_agent_details_to_package_dict_field(package_dict, 'publisher', org, False, meta_lang)
                    break
        except KeyError:
            pass

    # Dataset rights holder
    # TODO
    try:
        for org in iso_values['responsible-organisation']:
            if 'owner' in org['role']:
                _set_agent_details_to_package_dict_field(package_dict, 'rights_holder', org, True, meta_lang)
                break
    except KeyError:
        pass

    # modified: Last known time when a research dataset or metadata about the research dataset
    # has been significantly modified.
    # date-updated: the date of last revision for the dataset
    # metadata-date: either creation or update date of metadata
    try:
        package_dict['modified'] = iso_values['date-updated'] or iso_values['metadata-date']
    except KeyError:
        pass

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
                package_dict['spatial'].append({'as_wkt': [polygon]})
    except KeyError:
        pass

    # Temporal extent, assumption is same index within temporal-extent-begin and -end are related
    # No dataset have had values on these.
    try:
        if len(iso_values['temporal-extent-begin']) == len(iso_values['temporal-extent-end']) and \
        len(iso_values['temporal-extent-begin']) > 0:
            package_dict['temporal'] = []
            for idx, val in enumerate(iso_values['temporal-extent-begin']):
                package_dict['temporal'].append({'start_date': val,
                                                'end_date': iso_values['temporal-extent-end'][idx]})
    except KeyError:
        pass

    # issued: Date of formal issuance for the dataset
    # date-released: date of publication of dataset
    try:
        if iso_values['date-released']:
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
        package_dict['provenance'].append({'description': {meta_lang: iso_values['lineage']}})
    except KeyError:
        pass

    if len(package_dict['creator']) == 0:
        del package_dict['creator']

    if len(package_dict['curator']) == 0:
        del package_dict['curator']

    return package_dict


def _set_agent_details_to_package_dict_field(package_dict, field, agent, is_array, meta_lang):
    try:
        # Assuming that if individual-name exists in source data, the type is Person. Otherwise type is Organization.
        # Nothing in source data indicates whether the email address is personal or not
        # There is always organisation name included regardless of whether the email address is personal or not

        if agent.get('individual-name', False):
            type = 'Person'
        else:
            type = 'Organization'

        name = agent.get('individual-name', '') or agent.get('organisation-name', '')
        email = agent['contact-info'].get('email', '') if 'contact-info' in agent else ''

        member_of = None
        if type == 'Person' and agent.get('organisation-name', ''):
            member_of = {
                '@type': 'Organization',
                'name': {meta_lang: agent.get('organisation-name')}
            }

        if type == 'Person':
            name = name
        else:
            name = {meta_lang: name}
        agent_obj = {
            '@type': type,
            'name': name,
            'email': email,
        }

        if member_of:
            agent_obj.update({'member_of': member_of})

        if is_array:
            if field not in package_dict:
                package_dict[field] = []

            package_dict[field].append(agent_obj)

        else:
            package_dict[field] = agent_obj

    except Exception:
        raise
