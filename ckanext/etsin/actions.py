'''
Action overrides
'''

# For development use
import logging
log = logging.getLogger(__name__)

def package_create(context, data_dict):

    log.info("Greetings from within the Etsin package_create. Here's the dict I'm working with:")
    log.info(data_dict)

    # Return some dict (doesn't make sense yet)
    return data_dict


def package_delete(context, data_dict):
    return


def package_update(context, data_dict):
    return data_dict
