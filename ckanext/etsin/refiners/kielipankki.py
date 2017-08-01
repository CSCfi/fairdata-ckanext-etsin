'''
Refine Kielipankki data_dict
'''
from ckanext.etsin.cmdi_parse_helper import CmdiParseHelper

# For development use
import logging
log = logging.getLogger(__name__)

# Refines Kielipankki data_dict
# TODO: Not yet implemented


class KielipankkiRefiner():

    LICENSE_CLARIN_PUB = "CLARIN_PUB"
    LICENSE_CLARIN_ACA = "CLARIN_ACA"
    LICENSE_CLARIN_RES = "CLARIN_RES"
    LICENSE_CC_BY = "CC-BY"
    PID_PREFIX_URN = "urn.fi"

    @classmethod
    def _language_bank_license_enhancement(cls, license):
        """
        Enhance language bank licenses due to lacking source data
        so that Etsin understands them better.

        :param license: License
        :return:
        """
        output = license
        if license.startswith(cls.LICENSE_CC_BY):
            output = output + "-4.0"
        return output

    @classmethod
    def _language_bank_availability_from_license(cls, license):
        """
        Get availability from license for datasets harvested
        from language bank interface using the following rules:

        CLARIN_ACA-NC -> downloadable after registration / identification
        CLARIN_RES -> with data access application form
        CLARIN_PUB -> directly downloadable
        Otherwise -> only by contacting the distributor


        :param license: string value for the license
        :return: string value for availability
        """

        if license.startswith(cls.LICENSE_CLARIN_ACA):
            return "access_request"
        elif license == cls.LICENSE_CLARIN_RES:
            return "access_application_other"
        elif license == cls.LICENSE_CLARIN_PUB or license.startswith(cls.LICENSE_CC_BY):
            return "direct_download"
        else:
            return "contact_owner"

    @classmethod
    def _language_bank_urn_pid_enhancement(cls, pid):
        output = pid
        if pid.startswith(cls.PID_PREFIX_URN):
            output = 'http://' + pid
        return output


def kielipankki_refiner(data_dict):

    package_dict = data_dict

    # Things that should be added:
    # availability
    # pids

    # Read lxml object passed in from CMDI mapper
    xml = data_dict['context']['xml']
    helper = CmdiParseHelper(xml)

    license_identifier = KielipankkiRefiner._language_bank_license_enhancement(
        helper.parse_licence() or 'notspecified')
    availability = KielipankkiRefiner._language_bank_availability_from_license(
        license_identifier)

    direct_download_URL = ''
    access_request_URL = ''
    access_application_URL = ''
    if license_identifier.lower().strip() != 'undernegotiation':
        if availability == 'direct_download':
            direct_download_URL = primary_pid
        if availability == 'access_request':
            access_request_URL = primary_pid
        if availability == 'access_application_other':
            sliced_pid = primary_pid.rsplit('/', 1)
            if len(sliced_pid) >= 2:
                access_application_URL = 'https://lbr.csc.fi/web/guest/catalogue?domain=LBR&target=basket&resource=' + \
                    sliced_pid[1]

    # Refine the data
    package_dict.setdefault('remoteResources', {})
    package_dict['remoteResources'].update({
        "accessURL": {
            "identifier": "todo"    # TODO: access_request_URL or access_application_URL?
        },
        "downloadURL": {
            "identifier": direct_download_URL
        }
    })
#    package_dict.setdefault('accessRights', {})
#    package_dict['accessRights'] = {
#        "available": [
#
#        ]
#    }

    return package_dict
