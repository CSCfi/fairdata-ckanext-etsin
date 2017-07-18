import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.etsin import actions

class EtsinPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IActions)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'etsin')

    # IActions

    def get_actions(self):
        """ Register actions. """
        return {
            'package_create': actions.package_create,
        }
