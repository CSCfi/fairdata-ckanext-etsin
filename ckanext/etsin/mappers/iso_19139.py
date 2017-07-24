'''
Map ISO 19139 dicts to Metax values
'''

# For development use
import logging
log = logging.getLogger(__name__)

# Overwrites ckanext-spatial's get_package_dict
# TODO: Not yet implemented
def iso_19139_mapper(self, context, data_dict):

    package_dict = data_dict['package_dict']

    log.info("Greetings from within the spatial mapper. Here's the dict I'm working with:")
    log.info(package_dict)

    # Let's assume that Metax expects a key named "metax-title".
    # We can edit values given by ckanext-spatial's default get_package_dict
    package_dict['metax-title'] = package_dict['title']
    package_dict.pop('title', None)

    # We can also derive values from ISO values, XML tree or harvest object
    package_dict['metax-abstract'] = data_dict['iso_values']['abstract']

    log.info("And here's the dict after I mapped it to (demo) Metax format")
    log.info(package_dict)    

    return package_dict
