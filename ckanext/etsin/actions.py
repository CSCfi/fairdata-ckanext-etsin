'''
Action overrides
'''

import ckanext.etsin.metax_api as metax_api
import ckanext.etsin.refine

# For development use
import logging
log = logging.getLogger(__name__)

def package_create(context, data_dict):
    '''
    Refines data_dict. Calls Metax API to create new dataset.
    '''

    # Refine data_dict based on organization it belongs to
    data_dict = refine(data_dict)

    # Check with Metax if we should be creating or updating and do that
    # TODO: We may need to catch an error here
    _create_or_update(data_dict)

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

    return True


def package_update(context, data_dict):
    '''
    Refines data_dict. Calls Metax API to update an existing dataset.
    '''

    # Refine data_dict based on organization it belongs to
    data_dict = refine(data_dict)

    # Check with Metax if we should be creating or updating and do that
    # TODO: We may need to catch an error here
    _create_or_update(data_dict)

    return data_dict


def _create_or_update(data_dict):

    # Ask Metax if this dataset exists
    # TODO: This is the function that will be created in CSCETSIN-22
    if metax_api.ask_metax_whether_package_exists(data_dict['id']):
        # Metax says the package exists
        # TODO: may need to catch an error
        metax_api.replace_dataset(data_dict['metax-id'], data_dict)

    else:
        # Metax says the package doesn't exist
        # TODO: may need to catch an error
        metax_api.create_dataset(data_dict)

