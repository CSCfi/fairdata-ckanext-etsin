'''
Action overrides
'''
import logging

from requests import HTTPError
from requests.exceptions import ReadTimeout

import ckanext.etsin.metax_api as metax_api
from ckanext.etsin.refine import refine
from ckanext.etsin.utils import convert_to_metax_dict

import ckan.model as model
import ckan.logic.action.create
import ckan.logic.action.update
from ckan.lib.navl.validators import not_empty
from ckanext.etsin.exceptions import DatasetFieldsMissingError

log = logging.getLogger(__name__)

package_schema = {
    'id': [not_empty, unicode],
    'name': [not_empty, unicode]
}


def _create_package_to_metax(context, data_dict, package_id):
    pref_id = data_dict.get('preferred_identifier', None)
    # Create the dataset in MetaX
    if pref_id:
        try:
            log.info("Trying to create package to MetaX having preferred_identifier: %s", pref_id)
            md = convert_to_metax_dict(data_dict, context)
            log.info("metax_dict: {0}".format(md))
            metax_urn_id = metax_api.create_dataset(md)
            log.info("Created package to MetaX successfully. MetaX urn_identifier: %s", metax_urn_id)
        except HTTPError as e:
            log.error("Failed to create package to MetaX for a package having package ID: {0} "
                      "and preferred_identifier: {1}, error: {2}".format(package_id, pref_id, repr(e)))
            return None
        except ReadTimeout as e:
            log.error("Connection timeout: {0}".format(repr(e)))
            return None
    else:
        log.error("Package does not have a preferred identifier. Skipping.")
        return None
    return metax_urn_id


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
        # Get the package_id for the dict
        package_id = data_dict.pop('id')

        if not package_id:
            log.error("Package id not found in package_create from data_dict. Aborting..")
            return False

        # Refine data_dict based on organization it belongs to
        try:
            data_dict = refine(context, data_dict)
            # log.error("!!!!!!!!!!!!!!!!")
            # log.error(data_dict)
            # log.error("????????????????")
            # return False
        except DatasetFieldsMissingError as e:
            log.error(e)
            return False

        metax_urn_id = _create_package_to_metax(context, data_dict, package_id)
        if not metax_urn_id:
            return False

        # Create the package in our CKAN database
        context['schema'] = package_schema
        log.info("Trying to create package to CKAN database with id: %s and name: %s", package_id, metax_urn_id)
        output = ckan.logic.action.create.package_create(context, _get_data_dict_for_ckan_db(package_id, metax_urn_id))
        log.info("Created package to CKAN database successfully with id: %s and name: %s", package_id, metax_urn_id)
    else:
        output = ckan.logic.action.create.package_create(context, data_dict)

    return output


def package_update(context, data_dict):
    """
    Refines data_dict. Calls MetaX API to update an existing dataset.
    If successful updating to Metax, update dataset to CKAN db.
    Call the method as 'harvest' user only when harvesting datasets.
    In other cases (e.g. creating harvest source) do NOT use 'harvest' user
    """

    user = model.User.get(context['user'])

    if user.name == "harvest":
        # Get the package_id for the dict
        package_id = data_dict.pop('id')

        if not package_id:
            log.error("Package id not found in package_update from data_dict. Aborting..")
            return False

        # Refine data_dict based on organization it belongs to
        try:
            data_dict = refine(context, data_dict)
            # log.error("!!!!!!!!!!!!!!!!")
            # log.error(data_dict)
            # log.error("????????????????")
        except DatasetFieldsMissingError as e:
            log.error(e)
            return False

        # Get metax urn_identifier from ckan database
        metax_urn_id = _get_metax_id_from_ckan_db(package_id)

        if metax_api.check_dataset_exists(metax_urn_id):

            # Update the dataset in MetaX
            try:
                log.info("Trying to update package to MetaX having MetaX ID: %s", metax_urn_id)
                metax_api.update_dataset(metax_urn_id, convert_to_metax_dict(data_dict, context, metax_urn_id))
                log.info("Updated package to MetaX successfully having MetaX ID: %s", metax_urn_id)
            except HTTPError:
                log.error("Failed to update package to MetaX for a package having package ID: %s and MetaX ID: %s",
                          package_id, metax_urn_id)
                return False
            except ReadTimeout as e:
                log.error("Connection timeout: {0}".format(repr(e)))
                return False
        else:
            # Dataset does not exist in Metax even though it has been stored to local db
            # Most likely because the Metax target env has been emptied
            log.warn("Dataset with metax_urn_id {0} was not found from MetaX even though it exists in CKAN database".format(metax_urn_id))
            log.info("Trying to recreate package to MetaX and update package name into CKAN database to new metax_urn_id")
            metax_urn_id = _create_package_to_metax(context, data_dict, package_id)
            if not metax_urn_id:
                return False

        # Update the package in our CKAN database
        context['schema'] = package_schema
        log.info("Trying to update package to CKAN database with id: %s and name: %s", package_id, metax_urn_id)
        output = ckan.logic.action.update.package_update(context, _get_data_dict_for_ckan_db(package_id, metax_urn_id))
        log.info("Updated package to CKAN database successfully with id: %s and name: %s", package_id, metax_urn_id)
    else:
        output = ckan.logic.action.update.package_update(context, data_dict)

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
        # Get the package_id for the dict
        package_id = data_dict.pop('id')

        if not package_id:
            log.error("Package id not found in package_delete from data_dict. Aborting..")
            return False

        # Get metax urn_identifier from ckan database
        metax_urn_id = _get_metax_id_from_ckan_db(package_id)

        if metax_api.check_dataset_exists(metax_urn_id):
            try:
                log.info("Trying to delete package from MetaX having MetaX ID: %s", metax_urn_id)
                metax_api.delete_dataset(metax_urn_id)
                log.info("Deleted package from MetaX successfully having MetaX ID: %s", metax_urn_id)
            except HTTPError:
                log.error("Failed to delete package from MetaX for a package having package ID: %s and MetaX ID: %s",
                      package_id, metax_urn_id)
                return False
            except ReadTimeout as e:
                log.error("Connection timeout: {0}".format(repr(e)))
                return False
        else:
            log.warn("Dataset with metax_urn_id {0} was not found from MetaX even though it exists in CKAN database".format(metax_urn_id))
            log.info("Skipping delete operation in MetaX")

        package_dict = _get_data_dict_for_ckan_db(package_id, metax_urn_id)
        log.info("Trying to delete package from CKAN database with id: %s and name: %s", package_id, metax_urn_id)
        package_dict = ckan.logic.action.delete.package_delete(context, package_dict)
        log.info("Deleted package from CKAN database successfully with id: %s and name: %s", package_id, metax_urn_id)
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

