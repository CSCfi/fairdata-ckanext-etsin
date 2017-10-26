import logging
import os

from ckanext.etsin.data_catalog_service import DataCatalogMetaxAPIService as DCS
from ckanext.etsin.exceptions import DatasetFieldsMissingError
from ckanext.etsin.utils import set_existing_kata_identifier_to_other_identifier

log = logging.getLogger(__name__)


# Refines Syke data_dict
def syke_refiner(context, package_dict):
    data_catalog = DCS.get_data_catalog_from_file('syke_data_catalog.json')['catalog_json']

    # Field of science
    field_of_science = data_catalog['field_of_science'][0]
    package_dict['field_of_science'] = [{'identifier': field_of_science['identifier']}]

    # Fix email addresses
    # TODO: Verify from syke this is ok
    if 'curator' in package_dict:
        _fix_email_address(package_dict, 'curator')
    if 'creator' in package_dict:
        _fix_email_address(package_dict, 'creator')
    if 'publisher' in package_dict:
        _fix_email_address(package_dict, 'publisher')
    if 'rights_holder' in package_dict:
        _fix_email_address(package_dict, 'rights_holder')

    # Set license to "other" since only access rights description is available in the source metadata
    if 'access_rights' in package_dict and 'description' in package_dict['access_rights']:
        package_dict['access_rights']['license'] = [{
            'identifier': 'http://purl.org/att/es/reference_data/license/license_other'
        }]

    # Set access type to "restricted" since it is the only safe bet. Unless someone tells otherwise
    if 'access_rights' in package_dict and 'description' in package_dict['access_rights']:
        package_dict['access_rights']['type'] = [{
            'identifier': 'http://purl.org/att/es/reference_data/access_type/access_type_restricted_access'
        }]

    if 'guid' in context:
        set_existing_kata_identifier_to_other_identifier(
            os.path.dirname(__file__) + '/resources/syke_guid_to_kata_urn.csv', context['guid'], package_dict)

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
