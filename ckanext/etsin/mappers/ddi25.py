from functionally import first

# For development use
import logging
log = logging.getLogger(__name__)


def ddi25_mapper(xml):
    """ Convert given DDI 2.5 XML into MetaX format dict.
    :param xml: xml element (lxml)
    :return: dictionary
    """

    namespaces = {'oai': "http://www.openarchives.org/OAI/2.0/",
                  'ddi': "ddi:codebook:2_5"}

    cb = first(xml.xpath('//oai:record/oai:metadata/ddi:codeBook', namespaces=namespaces))
    stdy = cb.find('ddi:stdyDscr', namespaces)
    stdy = cb.xpath('//ddi:stdyDscr', namespaces=namespaces)[0]

    # Preferred identifier will be added in refinement
    preferred_identifier = None

    # Modified
    ver_stmt = stdy.find('ddi:citation/ddi:verStmt/ddi:version', namespaces)
    if ver_stmt:
        modified = ver_stmt.get('date')

    package_dict = {
        "preferred_identifier": preferred_identifier,
        "modified": modified,
        "title": [],
        "description": [],
        "language": [],
        "provenance": [{
            "temporal": {
                "startDate": "",
                "endDate": ""}}],
        "access_rights": {
            "available": "TODO: metadataCreationDate?",
            "description": [{
                "en": "TODO: Free account of the rights. This could be licenceInfo/attributionText"}], }}

    return package_dict
