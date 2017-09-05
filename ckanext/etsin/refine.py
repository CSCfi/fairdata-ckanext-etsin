'''
Chooses and calls a refiner function
'''

# import ckanext.etsin.refiners as refiners
import ckanext.etsin.refiners.kielipankki as kielipankki
import ckanext.etsin.refiners.syke as syke

# For development use
import logging
log = logging.getLogger(__name__)


def refine(context, data_dict):
    '''
    Chooses refiner function based on organization.
    '''

    # TODO: This assignment probably doesn't work, because organization is a CKAN object and not a string.
    # What's actually needed is the name of the organization. Fix this when actually implementing.
    organization = data_dict.get('organization', None)
    #organization = 'kielipankki'

    if organization == "kielipankki":
        data_dict = kielipankki.kielipankki_refiner(context, data_dict)
    elif organization == "syke":
        data_dict = syke.syke_refiner(context, data_dict)
    else:
        # TODO: Throw error
        #return False
        pass # For testing

    return data_dict
