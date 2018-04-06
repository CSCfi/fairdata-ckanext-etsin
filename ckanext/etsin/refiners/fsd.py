"""
Refine FSD data_dict
"""
from functionally import first

from ..utils import (convert_language,
                     get_language_identifier,
                     get_tag_lang)

# For development use
import logging
log = logging.getLogger(__name__)


def fsd_refiner(context, data_dict):
    """ Refines the given MetaX data dict in a FSD-specific way

    :param context: Dictionary with an lxml-field
    :param data_dict: Dataset dictionary in MetaX format
    """
    namespaces = {'oai': "http://www.openarchives.org/OAI/2.0/",
                  'ddi': "ddi:codebook:2_5"}

    package_dict = data_dict
    xml = context.get('source_data')
    cb = first(xml.xpath('//oai:record/oai:metadata/ddi:codeBook', namespaces=namespaces))

    # Language
    languages = [get_tag_lang(fn) for fn in cb.findall(
        'ddi:fileDscr/ddi:fileTxt/ddi:fileName', namespaces)]

    language_list = [{'identifier': get_language_identifier(
        convert_language(lang))} for lang in languages]

    package_dict['language'] = language_list

    return package_dict
