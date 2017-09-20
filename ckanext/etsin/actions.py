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
    return_id_only = context.get('return_id_only', False)

    if user.name == "harvest":
        # Get the package_id for the dict. Corresponds to harvest_object's guid
        package_id = data_dict.pop('id')

        # Refine data_dict based on organization it belongs to
        data_dict = refine(context, data_dict)

        pref_id = data_dict.get('preferred_identifier', None)
        # Create the dataset in MetaX
        if pref_id:
            try:
                log.info("Trying to create package to MetaX having preferred_identifier: %s", pref_id)
                metax_id = metax_api.create_dataset(convert_to_metax_dict(data_dict, context))
                log.info("Created package to MetaX successfully. MetaX ID: %s", metax_id)
            except HTTPError:
                log.error("Failed to create package to MetaX for a package having package ID: %s and preferred_identifier: %s", package_id, pref_id)
                return False
        else:
            log.error("Package does not have a preferred identifier. Skipping.")
            return False

        # Create the package in our CKAN database
        context['schema'] = package_schema
        log.info("Trying to Create package to CKAN database with id: %s and name: %s", package_id, metax_id)
        package_dict = ckan.logic.action.create.package_create(context, _get_data_dict_for_ckan_db(package_id, metax_id))
        log.info("Created package to CKAN database successfully with id: %s and name: %s", package_id, metax_id)

        # TODO: Do we need to index the package?
    else:
        package_dict = ckan.logic.action.create.package_create(context, data_dict)

    output = package_dict['id'] if return_id_only else package_dict
    return output


def package_update(context, data_dict):
    """
    Refines data_dict. Calls MetaX API to update an existing dataset.
    If successful updating to Metax, update dataset to CKAN db.
    Call the method as 'harvest' user only when harvesting datasets.
    In other cases (e.g. creating harvest source) do NOT use 'harvest' user
    """

    user = model.User.get(context['user'])
    return_id_only = context.get('return_id_only', False)

    if user.name == "harvest":
        # Get the package_id for the dict. Corresponds to harvest_object's guid
        package_id = data_dict.pop('id')

        # Refine data_dict based on organization it belongs to
        data_dict = refine(context, data_dict)

        log.info(data_dict)

        # Get metax_id from ckan database
        metax_id = _get_metax_id_from_ckan_db(package_id)

        # Update the dataset in MetaX
        try:
            log.info("Trying to update package to MetaX having MetaX ID: %s", metax_id)
            metax_api.replace_dataset(metax_id, convert_to_metax_dict(data_dict, context, metax_id))
            log.info("Updated package to MetaX successfully having MetaX ID: %s", metax_id)
        except HTTPError:
            log.error("Failed to update package to MetaX for a package having package ID: %s and MetaX ID: %s",
                      package_id, metax_id)
            return False

        # Update the package in our CKAN database
        context['schema'] = package_schema
        log.info("Trying to update package to CKAN database with id: %s and name: %s", package_id, metax_id)
        package_dict = ckan.logic.action.update.package_update(context, _get_data_dict_for_ckan_db(package_id, metax_id))
        log.info("Updated package to CKAN database successfully with id: %s and name: %s", package_id, metax_id)

        # TODO: Do we need to index the package?
    else:
        package_dict = ckan.logic.action.update.package_update(context, data_dict)

    output = package_dict['id'] if return_id_only else package_dict
    return output


def package_delete(context, data_dict):
    """
    Calls MetaX API to delete a dataset.
    If successful deleting from Metax, delete dataset from CKAN db.
    Call the method as 'harvest' user only when harvesting datasets.
    In other cases (e.g. creating harvest source) do NOT use 'harvest' user
    """

    user = model.User.get(context['user'])
    return_id_only = context.get('return_id_only', False)

    if user.name == "harvest":
        # Get the package_id for the dict. Corresponds to harvest_object's guid
        package_id = data_dict.pop('id')

        # Get metax_id from ckan database
        metax_id = _get_metax_id_from_ckan_db(package_id)

        try:
            log.info("Trying to delete package from MetaX having MetaX ID: %s", metax_id)
            metax_api.delete_dataset(metax_id)
            log.info("Deleted package from MetaX successfully having MetaX ID: %s", metax_id)
        except HTTPError:
            log.error("Failed to delete package from MetaX for a package having package ID: %s and MetaX ID: %s",
                  package_id, metax_id)
            return False

        package_dict = _get_data_dict_for_ckan_db(package_id, metax_id)
        log.info("Trying to delete package from CKAN database with id: %s and name: %s", package_id, metax_id)
        package_dict = ckan.logic.action.delete.package_delete(context, package_dict)
        log.info("Deleted package from CKAN database successfully with id: %s and name: %s", package_id, metax_id)

        # TODO: Do we need to index the package?
    else:
        package_dict = ckan.logic.action.delete.package_delete(context, data_dict)

    output = package_dict['id'] if return_id_only else package_dict
    return output


def _get_metax_id_from_ckan_db(package_id):
    return model.Session.query(model.Package) \
                        .filter(model.Package.id == package_id) \
                        .first() \
                        .name


def _get_data_dict_for_ckan_db(package_id, metax_id):
    return {
        'id': package_id,
        'name': metax_id
    }


def _dataset_exists_in_metax(data_dict):
    dataset_id = data_dict['preferred_identifier']
    return metax_api.check_dataset_exists(dataset_id)
