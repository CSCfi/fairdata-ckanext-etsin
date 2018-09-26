# This file is part of the Etsin harvester service
#
# Copyright 2017-2018 Ministry of Education and Culture, Finland
#
# :author: CSC - IT Center for Science Ltd., Espoo Finland <servicedesk@csc.fi>
# :license: GNU Affero General Public License version 3

"""
Refine Kielipankki data_dict
"""
import os
from ckanext.etsin.cmdi_parse_helper import CmdiParseHelper
from ckanext.etsin.utils import set_existing_kata_identifier_to_other_identifier
from ckanext.etsin.exceptions import DatasetFieldsMissingError

# For development use
import logging
log = logging.getLogger(__name__)


class KielipankkiRefiner():

    LICENSE_CLARIN_PUB = "CLARIN_PUB"
    LICENSE_CLARIN_ACA = "CLARIN_ACA"
    LICENSE_CLARIN_ACA_NC = "CLARIN_ACA-NC"
    LICENSE_CLARIN_RES = "CLARIN_RES"
    LICENSE_OTHER = "other"
    LICENSE_UNDERNEG = "underNegotiation"
    LICENSE_PROPRIETARY = "proprietary"
    LICENSE_CC_BY = "CC-BY"
    LICENSE_CC_BY_ND = "CC-BY-ND"
    LICENSE_CC_BY_SA = "CC-BY-SA"
    LICENSE_CC_BY_NC = "CC-BY-NC"
    LICENSE_CC_BY_NC_ND = "CC-BY-NC-ND"
    LICENSE_CC_BY_NC_SA = "CC-BY-NC-SA"

    license_mapping = {
        LICENSE_CLARIN_PUB: "ClarinPUB-1.0",
        LICENSE_CLARIN_ACA: "ClarinACA-1.0",
        LICENSE_CLARIN_ACA_NC: "ClarinACA+NC-1.0",
        LICENSE_CLARIN_RES: "ClarinRES-1.0",
        LICENSE_OTHER: "other",
        LICENSE_UNDERNEG: "undernegotiation",
        LICENSE_PROPRIETARY: "other",
        LICENSE_CC_BY: "CC-BY-4.0",
        LICENSE_CC_BY_ND: "CC-BY-ND-4.0",
        LICENSE_CC_BY_SA: "CC-BY-SA-4.0",
        LICENSE_CC_BY_NC: "CC-BY-NC-4.0",
        LICENSE_CC_BY_NC_ND: "CC-BY-NC-ND-4.0",
        LICENSE_CC_BY_NC_SA: "CC-BY-NC-SA-4.0"
    }

    PID_PREFIX_URN_FI = "urn.fi/"
    PID_PREFIX_HTTP_URN_FI = "http://urn.fi/"

    @classmethod
    def get_license(cls, license):
        """

        :param license: License from source data
        :return: License code Metax can understand
        """
        return cls.license_mapping.get(license, 'other')

    @classmethod
    def access_type_from_license(cls, license):
        """
        Get access type from license for datasets harvested
        from language bank interface using the following rules:

        CLARIN_ACA-NC -> downloadable after registration / identification
        CLARIN_RES -> with data access application form
        CLARIN_PUB -> directly downloadable
        Otherwise -> only by contacting the distributor


        :param license: string value for the license in the source data
        :return: string value for access type as it is in metax access_type reference data code field
        """

        if license == cls.LICENSE_CLARIN_ACA or license == cls.LICENSE_CLARIN_ACA_NC:
            return "restricted_access"
        elif license == cls.LICENSE_CLARIN_RES:
            return "restricted_access"
        elif license == cls.LICENSE_CLARIN_PUB or license.startswith(cls.LICENSE_CC_BY):
            return "open_access"
        else:
            return "restricted_access"

    @classmethod
    def urn_pid_enhancement(cls, pid):
        output = pid
        if output.startswith(cls.PID_PREFIX_URN_FI) or output.startswith(cls.PID_PREFIX_HTTP_URN_FI):
            output = output[(output.find(cls.PID_PREFIX_URN_FI) + len(cls.PID_PREFIX_URN_FI)):]
        return output


def kielipankki_refiner(context, data_dict):
    """ Refines the given MetaX data dict in a Kielipankki-specific way

    :param context: Dictionary with an lxml-field
    :param data_dict: Dataset dictionary in MetaX format
    """

    package_dict = data_dict
    xml = context.get('source_data')

    # Read lxml object passed in from CMDI mapper
    cmdi = CmdiParseHelper(xml)

    package_dict['access_rights'] = {}
    # License
    license_in_source_data = cmdi.parse_license() or 'notspecified'
    license_identifier = KielipankkiRefiner.get_license(license_in_source_data)
    package_dict['access_rights'].update({'license': [{'identifier': license_identifier}]})

    # Access type
    access_type_identifier = KielipankkiRefiner.access_type_from_license(license_in_source_data)
    package_dict['access_rights'].update({'access_type': {'identifier': access_type_identifier}})

    # Preferred identifier
    preferred_identifier = None
    for pid in [KielipankkiRefiner.urn_pid_enhancement(metadata_pid) for metadata_pid in cmdi.parse_metadata_identifiers()]:
        if 'urn' in pid and not preferred_identifier:
            preferred_identifier = pid
    if preferred_identifier is None:
        fbpid = KielipankkiRefiner.urn_pid_enhancement((cmdi.language_bank_fallback_identifier()[0]))
        if 'urn' in fbpid:
            preferred_identifier = fbpid
        else:
            raise DatasetFieldsMissingError(package_dict, msg="Could not find preferred identifier in the metadata")
    package_dict['preferred_identifier'] = preferred_identifier

    # Set field of science
    package_dict['field_of_science'] = [{"identifier": "http://www.yso.fi/onto/okm-tieteenala/ta6121"}]

    set_existing_kata_identifier_to_other_identifier(
            os.path.dirname(__file__) + '/resources/kielipankki_pid_to_kata_urn.csv',
            'http://urn.fi/{0}'.format(package_dict['preferred_identifier']), package_dict)

    # TODO: Language bank metadatas also have some relationInfo/(relationType/relatedResource)
    # If we are interested in enriching it with relation data

    return package_dict
