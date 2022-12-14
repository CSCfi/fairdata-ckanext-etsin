# coding=UTF8
#
# This file is part of the Etsin harvester service
#
# Copyright 2017-2018 Ministry of Education and Culture, Finland
#
# :author: CSC - IT Center for Science Ltd., Espoo Finland <servicedesk@csc.fi>
# :license: GNU Affero General Public License version 3

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
    ACCESS_RIGHTS = [{
        'match': r"The dataset is \(A\)",
        'license': 'other-open',
        'access_type': 'open'}, {
        'match': r"The dataset is \(B\)",
        'license': 'other-closed',
        'access_type': 'restricted',
        'restriction_grounds': ['education', 'research']}, {
        'match': r"The dataset is \(C\)",
        'license': 'other-closed',
        'access_type': 'restricted',
        'restriction_grounds': ['research']}, {
        'match': r"The dataset is \(D\)",
        'license': 'other-closed',
        'access_type': 'restricted'}]

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

    # Licence and access type
    if 'access_rights' not in package_dict:
        package_dict['access_rights'] = {}
    restriction = {}
    for res in cb.findall('ddi:stdyDscr/ddi:dataAccs/ddi:useStmt/ddi:restrctn',
                          namespaces):
        restriction[get_tag_lang(res)] = res.text.strip()
    if len(restriction.get('en', '')):
        for ar in ACCESS_RIGHTS:
            if re.match(ar['match'], restriction.get('en', '')):
                package_dict['access_rights']['license'] = [{
                    'identifier': ar['license'],
                    'description': restriction}]
                package_dict['access_rights']['access_type'] = {
                    'identifier': ar['access_type']}

                restriction_grounds = []
                for rg in ar.get('restriction_grounds', []):
                    restriction_grounds.append({'identifier': rg})
                if restriction_grounds:
                    package_dict['access_rights']['restriction_grounds'] = restriction_grounds

                break
        if package_dict['access_rights'].get('license') is None:
            log.error('Unknown licence in dataset')

    conditions = {}
    for cond in cb.findall('ddi:stdyDscr/ddi:dataAccs/ddi:useStmt/ddi:conditions',
                           namespaces):
        conditions[get_tag_lang(cond)] = cond.text.strip()
    if len(conditions):
        package_dict['access_rights']['description'] = conditions

    if 'access_type' not in package_dict['access_rights']:
        package_dict['access_rights']['access_type'] = {
            'identifier': 'http://uri.suomi.fi/codelist/fairdata/access_type/code/restricted'
        }

    # Add old pid
    old_pids_path = os.path.dirname(__file__) + '/resources/fsd_pid_to_kata_urn.csv'
    set_existing_kata_identifier_to_other_identifier(
        old_pids_path, package_dict['preferred_identifier'], package_dict)

    return package_dict
