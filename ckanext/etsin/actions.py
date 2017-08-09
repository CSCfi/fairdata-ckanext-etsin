'''
Action overrides
'''

import ckanext.etsin.metax_api as metax_api

from ckanext.etsin.refine import refine
import ckan.logic.action.create
import ckan.logic.action.update
import uuid

# TEMP
from ckan.lib.navl.validators import (ignore_missing,
                                      keep_extras,
                                      not_empty,
                                      empty,
                                      ignore,
                                      if_empty_same_as,
                                      not_missing,
                                      ignore_empty
                                      )
from ckan.logic.converters import (convert_user_name_or_id_to_id,
                                   convert_package_name_or_id_to_id,
                                   convert_group_name_or_id_to_id,
                                   convert_to_json_if_string,
                                   convert_to_list_if_string,
                                   remove_whitespace,
                                   extras_unicode_convert,
                                   )
from ckan.logic.validators import (
    package_id_not_changed,
    package_id_or_name_exists,
    name_validator,
    package_name_validator,
    package_version_validator,
    group_name_validator,
    tag_length_validator,
    tag_name_validator,
    tag_string_convert,
    duplicate_extras_key,
    ignore_not_package_admin,
    ignore_not_group_admin,
    ignore_not_sysadmin,
    no_http,
    user_name_validator,
    user_password_validator,
    user_both_passwords_entered,
    user_passwords_match,
    user_password_not_empty,
    isodate,
    int_validator,
    natural_number_validator,
    is_positive_integer,
    boolean_validator,
    user_about_validator,
    vocabulary_name_validator,
    vocabulary_id_not_changed,
    vocabulary_id_exists,
    object_id_validator,
    activity_type_exists,
    resource_id_exists,
    tag_not_in_vocabulary,
    group_id_exists,
    group_id_or_name_exists,
    owner_org_validator,
    user_name_exists,
    user_id_or_name_exists,
    role_exists,
    datasets_with_no_organization_cannot_be_private,
    list_of_strings,
    if_empty_guess_format,
    clean_format,
    no_loops_in_hierarchy,
    filter_fields_and_values_should_have_same_length,
    filter_fields_and_values_exist_and_are_valid,
    extra_key_not_in_root_schema,
    empty_if_not_sysadmin,
    package_id_does_not_exist,
)

# For development use
import logging
log = logging.getLogger(__name__)


def package_create(context, data_dict):
    '''
    Refines data_dict. Calls Metax API to create new dataset.

    :returns: package dictionary that was saved to CKAN db.
    '''

    # Refine data_dict based on organization it belongs to
    data_dict = refine(context, data_dict)

    # Check with Metax if we should be creating or updating and do that
    # TODO: We may need to catch an error here
    data_dict['id'] = unicode(uuid.uuid4())     # TEMP for package create
    metax_id = unicode(uuid.uuid4())            # TEMP
    metax_id = _create_or_update(data_dict)

    # Strip Metax data_dict to CKAN data_dict
    id = unicode(uuid.uuid4())
    data_dict = {
        'id': id,
        'name': metax_id
    }
    context['schema'] = {
        'id': [],
        'name': [not_empty, unicode, name_validator, package_name_validator]
    }

    # Copy and paste package creation from CKAN's original package_create
    log.info("Creating package: {}".format(data_dict))
    ckan.logic.action.create.package_create(context, data_dict)

    return data_dict


def package_delete(context, data_dict):
    '''
    Calls Metax API to delete a dataset.
    '''

    # TODO: Do we need to refine data_dict here? If there is any refiner that
    # changes package if, we need to refine here, too.

    # TODO: This is the function that will be created in CSCETSIN-22
    if metax_api.ask_metax_whether_package_exists(data_dict['id']):
        # Metax says the package exists
        # TODO: we may need to catch an error
        metax_api.delete_dataset(data_dict['metax-id'])

    # Copy and paste package deletion from CKAN's original package_delete

    return data_dict


def package_update(context, data_dict):
    '''
    Refines data_dict. Calls Metax API to update an existing dataset.
    '''

    # Refine data_dict based on organization it belongs to
    #data_dict = refine(data_dict)

    # Check with Metax if we should be creating or updating and do that
    # TODO: We may need to catch an error here
    #data_dict = _create_or_update(data_dict)

    # Strip Metax data_dict to CKAN data_dict
    #data_dict = _strip_data_dict(data_dict)

    # Copy and paste package updating from CKAN's original package_update
    ckan.logic.action.update.package_update(context, data_dict)

    return data_dict


def _create_or_update(data_dict):

    # Ask Metax if this dataset exists
    # TODO: This is the function that will be created in CSCETSIN-22
    # At this point I don't know if it returns True/False, ID or something else
    if metax_api.ask_metax_whether_package_exists(data_dict['id']):
        # Metax says the package exists
        # TODO: may need to catch an error
        metax_id = metax_api.replace_dataset(data_dict['metax-id'], data_dict)

    else:
        # Metax says the package doesn't exist
        # TODO: may need to catch an error
        metax_id = metax_api.create_dataset(data_dict)

    return id


def _strip_data_dict(data_dict, id):
    """ Turn the metax-formated dict into our CKAN format.

    :param data_dict: dictionary in MetaX format
    :param id: id to use on the returned dictionary
    :returns: dict that can be saved to CKAN db, with MetaX id in the name field
    """

    # Remove all fields not required in CKAN schema
    # Use metax id for name field, and generated id as id
    stripped_dict = {
        'name': data_dict['id'],
        'id': id
    }

    return stripped_dict
