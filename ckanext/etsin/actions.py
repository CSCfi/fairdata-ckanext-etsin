'''
Action overrides
'''

import ckanext.etsin.metax_api as metax_api
from ckanext.etsin.refine import refine
from ckanext.etsin.utils import convert_to_metax_dict

import ckan.model as model
import ckan.logic.action.create
import ckan.logic.action.update
from ckan.lib.navl.validators import not_empty
from ckan.logic.validators import name_validator

from requests import HTTPError

import logging
log = logging.getLogger(__name__)

package_schema = {
    'id': [not_empty, unicode],
    'name': [not_empty, unicode]
}


def package_create(context, data_dict):
    """
    Refines data_dict. Calls MetaX API to create a new dataset.
    If successful storing to Metax, store dataset to CKAN db.
    Call the method as 'harvest' user only when harvesting datasets.
    In other cases (e.g. creating harvest source) do NOT use 'harvest' user

    :returns: package dictionary that was saved to CKAN db.
    """
    user = model.User.get(context['user'])

    if user.name == "harvest":
        # Get the package_id for the dict. Corresponds to harvest_object's guid
        package_id = data_dict.pop('id')

        # Refine data_dict based on organization it belongs to
        #data_dict = refine(context, data_dict)

        # Create the dataset in MetaX
        try:
            log.info("Trying to create package to MetaX having preferred identifier: %s", data_dict['preferred_identifier'])
            metax_id = metax_api.create_dataset(convert_to_metax_dict(data_dict))
            log.info("Created package to MetaX having MetaX ID: %s", metax_id)
        except HTTPError:
            log.error("Failed to create package to MetaX for a package having package ID: %s", package_id)
            return False

        # Get data_dict for storing to CKAN db
        package_dict = _get_data_dict_for_ckan_db(package_id, metax_id)
        context['schema'] = package_schema

        # Create the package in our CKAN database
        log.info("Creating package to CKAN database with id: %s and name: %s", package_id, metax_id)
        package_dict = ckan.logic.action.create.package_create(context, package_dict)
        log.info("Created package with id: %s and name: %s", package_id, metax_id)

        # TODO: Do we need to index the package?
    else:
        package_dict = ckan.logic.action.create.package_create(context, data_dict)

    return package_dict


def package_update(context, data_dict):
    """
    Refines data_dict. Calls MetaX API to update an existing dataset.
    If successful updating to Metax, update dataset to CKAN db.
    Call the method as 'harvest' user only when harvesting datasets.
    In other cases (e.g. creating harvest source) do NOT use 'harvest' user
    """

    user = model.User.get(context['user'])

    if user.name == "harvest":
        # Get the package_id for the dict. Corresponds to harvest_object's guid
        package_id = data_dict.pop('id')

        # Refine data_dict based on organization it belongs to
        data_dict = refine(data_dict)

        # Get metax_id from ckan database
        metax_id = _get_metax_id_from_ckan_db(package_id)

        # Update the dataset in MetaX
        try:
            log.info("Trying to update package to MetaX having preferred identifier: %s", data_dict['preferred_identifier'])
            metax_api.replace_dataset(metax_id, convert_to_metax_dict(data_dict))
            log.info("Updated package to MetaX having MetaX ID: %s", metax_id)
        except HTTPError:
            log.error("Failed to update package to MetaX for a package having package ID: %s and MetaX ID: %s",
                      package_id, metax_id)
            return False

        # Get data_dict for storing to CKAN db
        package_dict = _get_data_dict_for_ckan_db(package_id, metax_id)
        context['schema'] = package_schema

        # Update the package in our CKAN database
        log.info("Updating package to CKAN database with id: %s and name: %s", package_id, metax_id)
        package_dict = ckan.logic.action.update.package_update(context, package_dict)
        log.info("Updated package with id: %s and name: %s", package_id, metax_id)

        # TODO: Do we need to index the package?
    else:
        package_dict = ckan.logic.action.update.package_update(context, data_dict)

    return package_dict


def package_delete(context, data_dict):
    """
    Calls MetaX API to delete a dataset.
    If successful deleting from Metax, delete dataset from CKAN db.
    Call the method as 'harvest' user only when harvesting datasets.
    In other cases (e.g. creating harvest source) do NOT use 'harvest' user
    """

    user = model.User.get(context['user'])

    if user.name == "harvest":
        # Get the package_id for the dict. Corresponds to harvest_object's guid
        package_id = data_dict.pop('id')

        # Get metax_id from ckan database
        metax_id = _get_metax_id_from_ckan_db(package_id)

        # TODO: This check for existence not necessarily needed?
        if _dataset_exists_in_metax(data_dict):
            try:
                log.info("Trying to delete package from MetaX having preferred identifier: %s", data_dict['preferred_identifier'])
                metax_api.delete_dataset(metax_id)
                log.info("Deleted package from MetaX having MetaX ID: %s", metax_id)
            except HTTPError:
                log.error("Failed to delete package from MetaX for a package having package ID: %s and MetaX ID: %s",
                      package_id, metax_id)
                return False

        package_dict = _get_data_dict_for_ckan_db(package_id, metax_id)
        log.info("Deleting package from CKAN database with id: %s and name: %s", package_id, metax_id)
        package_dict = ckan.logic.action.delete.package_delete(context, package_dict)
        log.info("Deleted package with id: %s and name: %s", package_id, metax_id)

        # TODO: Do we need to index the package?
    else:
        package_dict = ckan.logic.action.delete.package_delete(context, data_dict)

    return package_dict


def _get_metax_id_from_ckan_db(package_id):
    return model.Session.query(model.Package) \
                        .filter(model.Package.id == package_id) \
                        .first() \
                        .value('name')


def _get_data_dict_for_ckan_db(package_id, metax_id):
    return {
        'id': package_id,
        'name': metax_id
    }


def _dataset_exists_in_metax(data_dict):
    dataset_id = data_dict['preferred_identifier']
    return metax_api.check_dataset_exists(dataset_id)
