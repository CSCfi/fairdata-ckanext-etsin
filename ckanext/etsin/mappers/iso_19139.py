'''
Map ISO 19139 dicts to Metax values
'''

# For development use
import logging
log = logging.getLogger(__name__)

# Overwrites ckanext-spatial's get_package_dict
def iso_19139_mapper(self, context, data_dict):

    # log.info("Greetings from within the spatial mapper. Here's the dict I'm working with:")
    # log.info(data_dict)

    # Start with an empty slate
    package_dict = {}

    # Metax obligatory fields
    # Miika says these (and only these) are obligatory on 2017/08/14
    # Don't mind missing values

    try:
        # Use whatever id harvest source gives us
        package_dict['preferred_identifier'] = data_dict['iso_values']['guid']
    except KeyError:
        package_dict['preferred_identifier'] = ''

    try:
        # Harvest source only ever has one title, so no need to bother with language codes.
        package_dict['title'] = [{'default': data_dict['iso_values']['title']}]
    except KeyError:
        package_dict['title'] = [{'default': ''}]


    # log.info("And here's the dict after I mapped it to (demo) Metax format")
    # log.info(package_dict)    

    return package_dict
