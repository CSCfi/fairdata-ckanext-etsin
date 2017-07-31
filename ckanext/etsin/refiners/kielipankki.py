'''
Refine Kielipankki data_dict
'''

# For development use
import logging
log = logging.getLogger(__name__)

# Refines Kielipankki data_dict
# TODO: Not yet implemented


def kielipankki_refiner(data_dict):

    package_dict = data_dict

    # Things that should be added:
    # accessURL & downloadURL
    # availability
    # pids

    # Read lxml object passed in from CMDI mapper
    xml = data_dict['context']['xml']

    package_dict['remoteResources'] = {
        "accessURL": {

        },
        "downloadURL": {

        }
    }
    package_dict['accessRights'] = {
        "available": [
            
        ]
    }

    return package_dict
