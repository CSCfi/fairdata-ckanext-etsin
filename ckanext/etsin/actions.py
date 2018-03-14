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


def _create_catalog_record_to_metax(context, metax_rd_dict):
    """

    :param context:
    :param metax_rd_dict: contains the metadata for the MetaX catalog record research_dataset relation
    :param ckan_package_id: identifier that will be the id for the package in CKAN database in case catalog record
    is created successfully to MetaX
    :return: metadata_version_identifier of the catalog record if catalog record was successfully created to MetaX.
    Otherwise return None.
    """
    pref_id = metax_rd_dict.get('preferred_identifier', None)

    if pref_id:
        try:
            log.info("Trying to create a catalog record (CR) to MetaX having preferred_identifier {0}"
                     .format(pref_id))
            md = convert_to_metax_dict(metax_rd_dict, context)
            log.info("Payload to be sent to MetaX: {0}".format(md))
            metax_mvid = metax_api.create_catalog_record(md)
            log.info("Successfully created a CR to MetaX. Returned CR metadata_version_identifier: %s", metax_mvid)
        except HTTPError as e:
            log.error("Failed to create a CR to MetaX having preferred_identifier {0}, error: {1}"
                      .format(pref_id, repr(e)))
            return None
        except ReadTimeout as e:
            log.error("Connection timeout: {0}".format(repr(e)))
            return None
    else:
        log.error("Package does not have a preferred identifier. Skipping.")
        return None
    return metax_mvid


def package_create(context, metax_rd_dict):
    """
    Refines metax_rd_dict further with harvester source specific refiners. Calls MetaX API to create a new dataset.
    If successful storing to Metax, store dataset to CKAN database.
    Call the method as 'harvest' user only when harvesting datasets.
    In other cases (e.g. creating harvest source) do NOT use 'harvest' user

    :param metax_rd_dict: contains the metadata for the MetaX catalog record research_dataset relation
    :returns: package dictionary that was saved to CKAN db in case everything went well.
    """

    user = model.User.get(context['user'])

    if user.name == "harvest":
        # Get the package_id for the package dict
        ckan_package_id = metax_rd_dict.pop('id')

        if not ckan_package_id:
            log.error("CKAN package ID not found in package_create from data_dict. Aborting..")
            return False

        # Refine metax_rd_dict based on organization it belongs to
        try:
            metax_rd_dict = refine(context, metax_rd_dict)
        except DatasetFieldsMissingError as e:
            log.error(e)
            return False

        # Creating catalog record to MetaX should return catalog record metadata version identifier
        metax_mvid = _create_catalog_record_to_metax(context, metax_rd_dict)
        if not metax_mvid:
            return False

        # Create the package to CKAN database linking ckan_package_id and metax_mvid together
        context['schema'] = package_schema
        log.info("Trying to create package to CKAN database with ID: %s and name: %s", ckan_package_id, metax_mvid)
        output = ckan.logic.action.create.package_create(context, _get_data_dict_for_ckan_db(ckan_package_id, metax_mvid))
        log.info("Created package to CKAN database successfully with ID: %s and name: %s", ckan_package_id, metax_mvid)
    else:
        output = ckan.logic.action.create.package_create(context, metax_rd_dict)

    return output


def package_update(context, metax_rd_dict):
    """
    Refines metax_rd_dict further with harvester source specific refiners. Call MetaX API to update an existing dataset.
    If successful updating to Metax, update dataset to CKAN database.
    Call the method as 'harvest' user only when harvesting datasets.
    In other cases (e.g. creating harvest source) do NOT use 'harvest' user

    :param metax_rd_dict: contains the metadata for the MetaX catalog record research_dataset relation
    :returns: package dictionary that was saved to CKAN db in case everything went well.
    """

    user = model.User.get(context['user'])

    if user.name == "harvest":
        # Get the ckan_package_id for the dict
        ckan_package_id = metax_rd_dict.pop('id')

        if not ckan_package_id:
            log.error("Package id not found in package_update from data_dict. Aborting..")
            return False

        # Refine metax_rd_dict based on organization it belongs to
        try:
            metax_rd_dict = refine(context, metax_rd_dict)
        except DatasetFieldsMissingError as e:
            log.error(e)
            return False

        # Get MetaX metadata version identifier from CKAN database by searching for a package with given ckan_package_id
        metax_mvid = _get_metax_id_from_ckan_db(ckan_package_id)

        if metax_api.check_catalog_record_exists(metax_mvid):

            try:
                log.info("Trying to update catalog record (CR) to MetaX having metadata version identifier: %s",
                         metax_mvid)
                metax_api.update_catalog_record(metax_mvid, convert_to_metax_dict(metax_rd_dict, context, metax_mvid))
                log.info("Successfully updated CR to MetaX!")
            except HTTPError as e:
                log.error("Failed to update CR to MetaX having metadata version identifier {0} for a "
                          "CKAN package ID: {1}, error: {2}".format(metax_mvid, ckan_package_id, repr(e)))
                return False
            except ReadTimeout as e:
                log.error("Connection timeout: {0}".format(repr(e)))
                return False
        else:
            # CR does not exist in Metax even though it has been stored to local CKAN database
            # Most likely because the Metax target env has been emptied
            log.warning("CR with metadata_version_identifier {0} was not found from MetaX even though it "
                        "exists in CKAN database".format(metax_mvid))
            log.info("Trying to recreate package to MetaX and update package name into CKAN database with a new "
                     "MetaX metadata_version_identifier value")
            metax_mvid = _create_catalog_record_to_metax(context, metax_rd_dict)
            if not metax_mvid:
                return False

        # Update the package into CKAN database
        context['schema'] = package_schema
        log.info("Trying to update package to CKAN database with ID: %s and name: %s", ckan_package_id, metax_mvid)
        output = ckan.logic.action.update.package_update(context, _get_data_dict_for_ckan_db(ckan_package_id, metax_mvid))
        log.info("Updated package to CKAN database successfully with ID: %s and name: %s", ckan_package_id, metax_mvid)
    else:
        output = ckan.logic.action.update.package_update(context, metax_rd_dict)

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
        # Get the ckan_package_id for the dict
        ckan_package_id = data_dict.pop('id')

        if not ckan_package_id:
            log.error("Package id not found in package_delete from data_dict. Aborting..")
            return False

        # Get metax metadata_version_identifier from CKAN database
        metax_mvid = _get_metax_id_from_ckan_db(ckan_package_id)

        if metax_api.check_catalog_record_exists(metax_mvid):
            try:
                log.info("Trying to delete catalog record (CR) from MetaX having MetaX metadata version identifier: %s",
                         metax_mvid)
                metax_api.delete_catalog_record(metax_mvid)
                log.info("Successfully deleted package from MetaX!")
            except HTTPError:
                log.error("Failed to delete package from MetaX for a CR having CKAN package ID: %s and "
                          "MetaX metadata version identifier: %s", ckan_package_id, metax_mvid)
                return False
            except ReadTimeout as e:
                log.error("Connection timeout: {0}".format(repr(e)))
                return False
        else:
            log.warning("CR with metadata_version_identifier {0} was not found from MetaX even though it exists in "
                        "CKAN database".format(metax_mvid))
            log.info("Skipping delete operation in MetaX")

        package_dict = _get_data_dict_for_ckan_db(ckan_package_id, metax_mvid)
        log.info("Trying to delete package from CKAN database with ID: %s and name: %s", ckan_package_id, metax_mvid)
        package_dict = ckan.logic.action.delete.package_delete(context, package_dict)
        log.info("Successfully deleted package from CKAN database with ID: %s and name: %s",
                 ckan_package_id, metax_mvid)
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

