import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.etsin.mappers import iso_19139

from ckanext.etsin import actions
from ckanext.spatial.interfaces import ISpatialHarvester

import logging
log = logging.getLogger(__name__)

class EtsinPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(ISpatialHarvester)
    # plugins.implements(IOAIPMH) # TODO: This interface doesn't exist yet


    # IActions

    def get_actions(self):
        """ Register actions. """
        return {
            'package_create': actions.package_create,
            'package_delete': actions.package_delete,
            'package_update': actions.package_update,
        }


    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'etsin')


    # IOAIPMH
    # TODO: This interface has not been implemented in ckanext-oaipmh yet

    # def get_package_dict(self, context, format, data_dict):
    #     # OAI-PMH comes in several formats
    #     if format == "cmdi":        
    #         return mappers.cmdi_mapper(context, data_dict)
    #     else:
    #         # TODO: It would probably be better to raise an error here
    #         # and inform caller about invalid format
    #         return False


    # ISpatialHarvester

    def get_package_dict(self, context, data_dict):
        return iso_19139.iso_19139_mapper(context, data_dict)

    # This needs to be here - otherwise ckanext-spatial fails silently
    def get_validators(self):
        return []

