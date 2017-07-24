'''
Chooses and calls a refiner function
'''

import ckanext.etsin.refiners as refiners

# For development use
import logging
log = logging.getLogger(__name__)

def refine(data_dict):
    '''
    Chooses refiner function based on organization. 
    '''

    # TODO: This assignment probably doesn't work, because organization is a CKAN object and not a string. 
    # What's actually needed is the name of the organization. Fix this when actually implementing.
    organization = data_dict['organization']

    if organization == "kielipankki":
        data_dict = refiners.kielipankki_refiner(data_dict)
    elif organization == "syke":
        data_dict = refiners.syke_refiner(data_dict)
    else:
        # TODO: Throw error
        return False

    return data_dict
