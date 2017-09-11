from ckanext.etsin.scripts.data_catalog_service import get_data_catalog_from_file
# For development use
import logging
log = logging.getLogger(__name__)


# Refines Syke data_dict
def syke_refiner(context, package_dict):
    data_catalog = get_data_catalog_from_file('syke_data_catalog.json')['catalog_json']
    default_contact = data_catalog['publisher'][0]

    #Discipline / Field of science
    discipline = data_catalog['field_of_science'][0]
    package_dict['discipline'] = {'identifier': discipline['identifier']}

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

    # If curator or creator has not been set, force it from data catalog
    if 'curator' not in package_dict or not len(package_dict['curator']):
        package_dict['curator'] = [{'identifier': default_contact['identifier'],
                                    'name': default_contact['name']['fi']}]
    if not len(package_dict['creator']):
        package_dict['creator'] = [{'identifier': default_contact['identifier'],
                                    'name': default_contact['name']['fi']}]

    return package_dict


def _fix_email_address(package_dict, agent_type):
    if isinstance(package_dict[agent_type], list):
        for agent in package_dict[agent_type]:
            _replace_with_at(agent)
            _split_multi_email(package_dict, agent_type, agent)
    elif isinstance(package_dict[agent_type], object):
        agent = package_dict[agent_type]
        _replace_with_at(agent)
        _split_multi_email(package_dict, agent_type, agent)


def _replace_with_at(agent):
    agent['email'] = agent['email']. \
        replace('[at]', '@'). \
        replace('[a]', '@'). \
        replace(' ', '')


def _split_multi_email(package_dict, agent_type, agent):
    multi_email = agent['email'].split(';')
    if len(multi_email) > 1:
        package_dict[agent_type] = []
        for email in multi_email:
            package_dict[agent_type].append({'name': agent['name'], 'email': email})
