'''
Refine Kielipankki data_dict
'''
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
    LICENSE_CLARIN_RES = "CLARIN_RES"
    LICENSE_CC_BY = "CC-BY"
    LICENSE_UNDERNEG = "underNegotiation"
    PID_PREFIX_URN_FI = "urn.fi/"
    PID_PREFIX_HTTP_URN_FI = "http://urn.fi/"

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
        elif license.startswith(cls.LICENSE_UNDERNEG):
            output = output.lower()
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
            return "restricted_access_permit"
        elif license == cls.LICENSE_CLARIN_RES:
            return "restricted_access_permit"
        elif license == cls.LICENSE_CLARIN_PUB or license.startswith(cls.LICENSE_CC_BY):
            return "open_access"
        else:
            return "restricted_access"

    @classmethod
    def _language_bank_urn_pid_enhancement(cls, pid):
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

    license_identifier = KielipankkiRefiner._language_bank_license_enhancement(
        cmdi.parse_licence() or 'notspecified')
    availability = KielipankkiRefiner._language_bank_availability_from_license(
        license_identifier)
    package_dict['access_rights'] = {
        'license': [{'identifier': license_identifier}]}

    preferred_identifier = None
    for pid in [KielipankkiRefiner._language_bank_urn_pid_enhancement(metadata_pid) for metadata_pid in cmdi.parse_metadata_identifiers()]:
        if 'urn' in pid and not preferred_identifier:
            preferred_identifier = pid
    if preferred_identifier is None:
        fbpid = KielipankkiRefiner._language_bank_urn_pid_enhancement((cmdi.language_bank_fallback_identifier()[0]))
        if 'urn' in fbpid:
            preferred_identifier = fbpid
        else:
            raise DatasetFieldsMissingError(package_dict, msg="Could not find preferred identifier in the metadata")
    package_dict['preferred_identifier'] = preferred_identifier

    # Set access URLs
    if license_identifier.lower().strip() != 'undernegotiation':
        if availability == 'open_access':
            package_dict['remote_resources'] = [{
                'type': {'identifier': 'other'},
                'access_url': {'identifier': preferred_identifier},
                'title': 'View the resource in META-SHARE',
            }]

        if availability == 'restricted_access_permit' \
                and license_identifier.startswith(KielipankkiRefiner.LICENSE_CLARIN_ACA):
            package_dict['remote_resources'] = [{
                'type': {'identifier': 'other'},
                'access_url': {'identifier': preferred_identifier},
                'title': 'View the resource in META-SHARE',
            }]

        if availability == 'restricted_access_permit':
            sliced_pid = preferred_identifier.rsplit('/', 1)
            if len(sliced_pid) >= 2:
                package_dict['access_rights'] = {
                    'type': [{'identifier': availability}],
                    'has_rights_related_agent': [{
                        '@type': 'Agent',
                        'identifier': 'https://lbr.csc.fi/web/guest/catalogue?domain=LBR&target=basket&resource=' +
                                      sliced_pid[1],
                        'name': 'Language Bank Rights System'}]
                }
        else:
            package_dict['access_rights'] = {
                'type': [{
                    'identifier': availability}]
            }

    # Set field of science
    package_dict['field_of_science'] = [{"identifier": "http://www.yso.fi/onto/okm-tieteenala/ta6121"}]

    set_existing_kata_identifier_to_other_identifier(
            os.path.dirname(__file__) + '/resources/kielipankki_pid_to_kata_urn.csv',
            package_dict['preferred_identifier'], package_dict)

    return package_dict
