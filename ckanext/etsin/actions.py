'''
Action overrides
'''

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
    if ask_metax_whether_package_exists(data_dict['id']):
        # Metax says the package exists
        # TODO: This is the function that will be created in CSCETSIN-21
        # Also, we may need to catch an error
        delete_package_via_metax_api(data_dict)

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
    if ask_metax_whether_package_exists(data_dict['id']):
        # Metax says the package exists
        # TODO: This is the function that will be created in CSCETSIN-20
        # Also, we may need to catch an error
        update_package_via_metax_api(data_dict)

    else:
        # Metax says the package doesn't exist
        # TODO: This is the function that will be created in CSCETSIN-19
        # Also, we may need to catch an error
        create_package_via_metax_api(data_dict)


# TODO: These functions should not be implemented here.
# I'm only defining them for placeholding purposes.
# All these functions must log all the API calls we make and all the responses.
def ask_metax_whether_package_exists(id):
    pass

def create_package_via_metax_api(data_dict):
    pass

def update_package_via_metax_api(data_dict):
    pass

def delete_package_via_metax_api(data_dict):
    pass
