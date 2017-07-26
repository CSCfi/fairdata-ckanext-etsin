'''
Map ISO 19139 dicts to Metax values
'''

# For development use
import logging
log = logging.getLogger(__name__)

# Overwrites ckanext-spatial's get_package_dict
def iso_19139_mapper(self, context, data_dict):

    log.info("Greetings from within the spatial mapper. Here's the dict I'm working with:")
    log.info(data_dict)

    # Start with an empty slate
    package_dict = []

    # Metax obligatory fields
    package_dict['urn_identifier'] = "todo" # We can't rely on harvested packages having a URN identifier
    package_dict['preferred_identifier'] = "todo" # We can't rely on harvested packages having a URL/URN identifier
    package_dict['modified'] = data_dict['metadata_modified_date']
    package_dict['versionNotes'] = "" # We don't have any - is empty string ok?
    package_dict['title'] = [{"TODO": data_dict['iso_values']['title']}] # What language codec is used here? We may have it in ['extras']['metadata-language'], but no guarantees.
    package_dict['description'] = [{"TODO": data_dict['iso_values']['abstract']}] # Like above
    package_dict['totalbytesize'] = 0 # We don't have this information - is 0 ok or should here be another code?
    package_dict['ready_status'] = "Finished" # Can we always use "Finished" or do we have to use "Removed", too? When we call metax api delete, does it care about this value?
    package_dict['curator'] = [{"name": data_dict['iso_values']['responsible-organisation']['organisation-name']}] # I think this is where it should be. Syke uses ['iso-values']['responsible-party'] though.
    package_dict['creator'] = [{"name": ""}] # Not sure if ISO 19139 even has this information. There certainly are datasets that don't.
    package_dict['language'] = [{"title": ["TODO"], "identifier": "TODO"}] # Like above, we may need to use unknown language

    log.info("And here's the dict after I mapped it to (demo) Metax format")
    log.info(package_dict)    

    return package_dict
