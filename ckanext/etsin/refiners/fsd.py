"""
Refine FSD data_dict
"""

# For development use
import logging
log = logging.getLogger(__name__)


def fsd_refiner(context, data_dict):
    """ Refines the given MetaX data dict in a FSD-specific way

    :param context: Dictionary with an lxml-field
    :param data_dict: Dataset dictionary in MetaX format
    """

    package_dict = data_dict
    xml = context.get('source_data')

    return package_dict
