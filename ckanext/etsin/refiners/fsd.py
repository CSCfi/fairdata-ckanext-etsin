# coding=UTF8
"""
Refine FSD data_dict
"""
from functionally import first
import os
import re

from ..utils import (convert_language,
                     get_language_identifier,
                     get_tag_lang,
                     set_existing_kata_identifier_to_other_identifier)

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
    LICENSE_ID_A_FSD = 'other-open'
    LICENSE_ID_BCD_FSD = 'other-closed'

    package_dict = data_dict
    xml = context.get('source_data')
    cb = first(xml.xpath('//oai:record/oai:metadata/ddi:codeBook',
                         namespaces=namespaces))

    # Language
    languages = [get_tag_lang(fn) for fn in cb.findall(
        'ddi:fileDscr/ddi:fileTxt/ddi:fileName', namespaces)]

    language_list = [{'identifier': get_language_identifier(
        convert_language(lang))} for lang in languages]

    package_dict['language'] = language_list

    # Licence
    if 'access_rights' not in package_dict:
        package_dict['access_rights'] = {}
    restriction = {}
    for res in cb.findall('ddi:stdyDscr/ddi:dataAccs/ddi:useStmt/ddi:restrctn',
                          namespaces):
        restriction[get_tag_lang(res)] = res.text.strip()
    if len(restriction.get('en', '')):
        if re.match(r"The dataset is \([BCD]\)", restriction.get('en', '')):
            lic_id = LICENSE_ID_BCD_FSD
        elif re.match(r'The dataset is \(A\)', restriction.get('en', '')):
            lic_id = LICENSE_ID_A_FSD
        else:
            log.error('Unknown licence in dataset')
            lic_id = 'other'
        package_dict['access_rights']['license'] = [{
            'identifier': lic_id,
            'description': [restriction]}]

    conditions = {}
    for cond in cb.findall('ddi:stdyDscr/ddi:dataAccs/ddi:useStmt/ddi:conditions',
                           namespaces):
        conditions[get_tag_lang(cond)] = cond.text.strip()
    if len(conditions):
        package_dict['access_rights']['description'] = [conditions]

    # Add old pid
    old_pids_path = os.path.dirname(__file__) + '/resources/fsd_pid_to_kata_urn.csv'
    set_existing_kata_identifier_to_other_identifier(
        old_pids_path, package_dict['preferred_identifier'], package_dict)

    return package_dict
