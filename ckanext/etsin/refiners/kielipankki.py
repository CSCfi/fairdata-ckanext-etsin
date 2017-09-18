'''
Refine Kielipankki data_dict
'''
from ckanext.etsin.cmdi_parse_helper import CmdiParseHelper

# For development use
import logging
log = logging.getLogger(__name__)


class KielipankkiRefinerException(Exception):
    """ Reader exception is thrown on unexpected data or error. """
    pass


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
        if pid.startswith(cls.PID_PREFIX_URN):
            output = 'http://' + pid
        return output


def kielipankki_refiner(context, data_dict):
    """ Refines the given MetaX data dict in a Kielipankki-specific way

    :param context: Dictionary with an lxml-field
    :param data_dict: Dataset dictionary in MetaX format
    """

    package_dict = data_dict
    xml = context.get('xml')

    # Read lxml object passed in from CMDI mapper
    cmdi = CmdiParseHelper(xml)

    license_identifier = KielipankkiRefiner._language_bank_license_enhancement(
        cmdi.parse_licence() or 'notspecified')
    availability = KielipankkiRefiner._language_bank_availability_from_license(
        license_identifier)
    package_dict['access_rights'] = {
        'license': [{'identifier': license_identifier}]}

    pids = []
    preferred_identifier = None
    for pid in [KielipankkiRefiner._language_bank_urn_pid_enhancement(metadata_pid) for metadata_pid in cmdi.parse_metadata_identifiers()]:
        if 'urn' in pid and not preferred_identifier:
            pids.append(dict(id=pid, provider=cmdi.provider, type='primary'))
            preferred_identifier = pid
    if preferred_identifier is None:
        raise KielipankkiRefinerException("Could not find preferred identifier in the metadata")
    package_dict['preferred_identifier'] = preferred_identifier

    # Set access URLs
    package_dict.setdefault('remote_resources', [])
    package_dict.setdefault('access_rights', {})
    if license_identifier.lower().strip() != 'undernegotiation':
        if availability == 'open_access':
            package_dict['remote_resources'] = [{
                'type': [{'identifier': availability}],
                'access_url': {'identifier': preferred_identifier}
            }]

        if availability == 'restricted_access_permit' \
                and license_identifier.startswith(KielipankkiRefiner.LICENSE_CLARIN_ACA):
            package_dict['remote_resources'] = [{
                'type': [{'identifier': availability}],
                'access_url': {'identifier': preferred_identifier}
            }]

        if availability == 'restricted_access_permit':
            sliced_pid = preferred_identifier.rsplit('/', 1)
            if len(sliced_pid) >= 2:
                package_dict['access_rights'] = {
                    'type': [{'identifier': availability}],
                    'has_right_related_agent': [{'homepage': {
                        'identifier': 'https://lbr.csc.fi/web/guest/catalogue?domain=LBR&target=basket&resource=' +
                                      sliced_pid[1]}}]
                }
        else:
            package_dict['access_rights'] = {
                'type': [{
                    'identifier': availability}]
            }

    package_dict.setdefault('otherIdentifier', [])
    package_dict['otherIdentifier'].extend([{
        "notation": pid['id'],
        "localIdentifierType": "todo"
    } for pid in pids if pid['type'] != 'primary'])
#    package_dict.setdefault('accessRights', {})
#    package_dict['accessRights'] = {
#        "available": [
#
#        ]
#    }

    return package_dict
