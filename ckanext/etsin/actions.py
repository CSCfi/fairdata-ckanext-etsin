'''
Action overrides
'''

import ckanext.etsin.metax_api as metax_api

from ckanext.etsin.refine import refine
import ckan.logic.action.create
import ckan.logic.action.update
import uuid

from ckan.lib.navl.validators import (ignore_missing,
                                      not_empty,
                                      ignore_empty
                                      )
from ckan.logic.validators import (
    name_validator,
    package_name_validator
)
from requests import HTTPError

# For development use
import logging
log = logging.getLogger(__name__)

package_schema = {
    'id': [ignore_missing],
    'name': [not_empty, unicode, name_validator, package_name_validator]
}


def package_create(context, data_dict):
    """
    Refines data_dict. Calls MetaX API to create a new dataset.

    :returns: package dictionary that was saved to CKAN db.
    """

    # Get the package_id for the dict
    package_id = data_dict.pop('id')

    # Refine data_dict based on organization it belongs to
    data_dict = refine(context, data_dict)

    # Create or update the dataset in MetaX
    try:
        metax_id = _create_or_update(data_dict)
    except HTTPError:
        log.info("Failed to create or update package to MetaX: {}".format(data_dict))
        return False

    # Strip Metax data_dict to CKAN package_dict
    package_dict = {
        'id': package_id,
        'name': metax_id
    }
    context['schema'] = package_schema

    # Create the package in our CKAN database
    print "Creating package: {}".format(package_dict)
    package_dict = ckan.logic.action.create.package_create(
        context, package_dict)
    print "Created package:", package_dict

    return package_dict


def package_delete(context, data_dict):
    """
    Calls MetaX API to delete a dataset.
    """

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
    """
    Refines data_dict. Calls MetaX API to update an existing dataset.
    """

    # Refine data_dict based on organization it belongs to
    data_dict = refine(data_dict)

    # Check with Metax if we should be creating or updating and do that
    # TODO: We may need to catch an error here
    data_dict = _create_or_update(data_dict)

    # Strip Metax data_dict to CKAN data_dict
    data_dict = _strip_data_dict(data_dict)

    # Copy and paste package updating from CKAN's original package_update
    ckan.logic.action.update.package_update(context, data_dict)

    return data_dict


def _create_or_update(data_dict):
    """ Adds dataset to MetaX, or updates it if it already exists if necessary. """
    dataset_id = data_dict['preferred_identifier']
    exists_in_metax = metax_api.check_dataset_exists(dataset_id)
    if exists_in_metax:
        # Metax says the package exists
        # TODO: may need to catch an error

        # TODO: do we need to find & use previous harvest_object instead?
        # previous_harvest_object = model.Session.query(HarvestObject) \
        #     .filter(HarvestObject.guid == dataset_id) \
        #     .first()

        metax_id = model.Session.query(Package) \
            .filter(harvest_object.package_id) \
            .first() \
            .name

        metax_api.replace_dataset(metax_id, data_dict)

    else:
        # Metax says the package doesn't exist
        # TODO: may need to catch an error
        metax_id = metax_api.create_dataset(data_dict)

    return metax_id
