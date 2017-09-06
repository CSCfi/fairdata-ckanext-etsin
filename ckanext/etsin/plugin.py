import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.etsin.mappers import iso_19139
from ckanext.etsin.mappers import cmdi

from ckanext.etsin import actions
from ckanext.spatial.interfaces import ISpatialHarvester
from ckanext.oaipmh.interfaces import IOAIPMHHarvester

import logging
log = logging.getLogger(__name__)

class EtsinPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(ISpatialHarvester)
    plugins.implements(IOAIPMHHarvester)

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

    # IOAIPMHHarvester

    def get_oaipmh_package_dict(self, format, xml):
        # OAI-PMH comes in several formats
        if format == 'cmdi0571':
            return cmdi.cmdi_mapper(xml)
        else:
            return {}

    # ISpatialHarvester

    def get_package_dict(self, context, data_dict):
        return iso_19139.iso_19139_mapper(data_dict)

    # This needs to be here - otherwise ckanext-spatial fails silently
    def get_validators(self):
        return []

