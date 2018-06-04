# This file is part of the Etsin harvester service
#
# Copyright 2017-2018 Ministry of Education and Culture, Finland
#
# :author: CSC - IT Center for Science Ltd., Espoo Finland <servicedesk@csc.fi>
# :license: GNU Affero General Public License version 3

import logging
import os

from ckanext.etsin.data_catalog_service import DataCatalogMetaxAPIService as DCS
from ckanext.etsin.exceptions import DatasetFieldsMissingError
from ckanext.etsin.utils import search_pid_exists_in_mapping_file, \
                                set_existing_kata_identifier_to_preferred_identifier, \
                                set_urn_pid_to_other_identifier

log = logging.getLogger(__name__)


# Refines Syke data_dict
def syke_refiner(context, package_dict):
    mapping_file_path = os.path.dirname(__file__) + '/resources/syke_guid_to_kata_urn.csv'
    harvest_object_guid = context.get('guid', None)
    if not harvest_object_guid:
        log.error("Harvest object must have guid. Skipping.")
        return None

    # Special rule, which is to be removed when syke gets their own resolvable identifiers to their datasets:
    # Do not harvest datasets which do / did not exist in old etsin and set existing kata identifier to dataset
    # preferred_identifier field
    if not search_pid_exists_in_mapping_file(mapping_file_path, harvest_object_guid):
        log.warning("Harvest object guid {0} not found from the mapping file. Skipping harvesting for now..".
                    format(harvest_object_guid))
        return None

    set_existing_kata_identifier_to_preferred_identifier(mapping_file_path, harvest_object_guid, package_dict)
    set_urn_pid_to_other_identifier(harvest_object_guid, package_dict)

    data_catalog = DCS.get_data_catalog_from_file('syke_data_catalog.json')['catalog_json']

    # If Field of science was not set in mapper, fallback here to syke data catalog fos
    if 'field_of_science' not in package_dict or not len(package_dict.get('field_of_science')):
        field_of_science = data_catalog['field_of_science'][0]
        package_dict['field_of_science'] = [{'identifier': field_of_science['identifier']}]

    # Fix email addresses
    if 'curator' in package_dict:
        _fix_email_address(package_dict, 'curator')
    if 'creator' in package_dict:
        _fix_email_address(package_dict, 'creator')
    if 'publisher' in package_dict:
        _fix_email_address(package_dict, 'publisher')
    if 'rights_holder' in package_dict:
        _fix_email_address(package_dict, 'rights_holder')

    if 'access_rights' not in package_dict:
        package_dict['access_rights'] = {}

    if 'description' in package_dict and len(package_dict.get('description', [])):
        description = package_dict['description'][0].values()[0]

        if 'CC BY 4.0' in description:
            package_dict['access_rights']['license'] = [{'identifier': 'CC-BY-4.0'}]
            package_dict['access_rights']['access_type'] = {
                'identifier': 'http://purl.org/att/es/reference_data/access_type/access_type_open_access'
            }

    if 'license' not in package_dict['access_rights']:
        package_dict['access_rights']['license'] = [{'identifier': 'other'}]

    if 'access_type' not in package_dict['access_rights']:
        package_dict['access_rights']['access_type'] = {
            'identifier': 'http://purl.org/att/es/reference_data/access_type/access_type_restricted_access'
        }

    _check_for_required_fields(package_dict)

    return package_dict


def _check_for_required_fields(package_dict):
    if 'preferred_identifier' not in package_dict or not package_dict['preferred_identifier']:
        raise DatasetFieldsMissingError(package_dict)
    if 'title' not in package_dict or not package_dict['title']:
        raise DatasetFieldsMissingError(package_dict)


def _fix_email_address(package_dict, agent_role):
    if isinstance(package_dict[agent_role], list):
        for agent in package_dict[agent_role]:
            _replace_with_at(agent)
            _split_multi_email(package_dict, agent_role, agent, False)
    elif isinstance(package_dict[agent_role], object):
        agent = package_dict[agent_role]
        _replace_with_at(agent)
        _split_multi_email(package_dict, agent_role, agent, True)


def _replace_with_at(agent):
    agent['email'] = agent['email']. \
        replace('[at]', '@'). \
        replace('[a]', '@'). \
        replace(' ', '')


def _split_multi_email(package_dict, agent_role, agent, choose_first_in_multi_email):
    multi_email = agent['email'].split(';')
    if len(multi_email) > 1:
        if choose_first_in_multi_email:
            package_dict[agent_role] = {}
        else:
            package_dict[agent_role] = []

        for email in multi_email:
            new_agent = {'@type': agent['@type'], 'name': agent['name'], 'email': email}
            if choose_first_in_multi_email:
                package_dict[agent_role].update(new_agent)
                break
            else:
                package_dict[agent_role].append(new_agent)
