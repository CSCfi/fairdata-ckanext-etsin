import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.etsin import actions, mappers
from ckanext.spatial.interfaces import ISpatialHarvester

class EtsinPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(ISpatialHarvester)

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

    # ISpatialHarvester

    def get_package_dict(self, context, data_dict):
        # TODO "spatial" is not a good function name
        return mappers.spatial(context, data_dict)
