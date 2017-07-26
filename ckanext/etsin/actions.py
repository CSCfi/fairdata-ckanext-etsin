'''
Action overrides
'''

import ckanext.etsin.metax_api as metax_api

from ckanext.etsin.refine import refine

# For development use
import logging
log = logging.getLogger(__name__)

def package_create(context, data_dict):
    '''
    Refines data_dict. Calls Metax API to create new dataset.
    '''

    # Refine data_dict based on organization it belongs to
    data_dict = refine(data_dict)

    # Just for testing
    log.info("Greetings from within the Etsin package_create. Here's the dict I'm working with:")
    log.info(data_dict)

    return data_dict


def package_delete(context, data_dict):
    '''
    Calls Metax API to delete a dataset.
    '''

    # TODO: Do we need to refine data_dict here? If there is any refiner that 
    # changes package if, we need to refine here, too.

    return


def package_update(context, data_dict):
    '''
    Refines data_dict. Calls Metax API to update an existing dataset.
    '''

    # Refine data_dict based on organization it belongs to
    data_dict = refine(data_dict)

    return data_dict
