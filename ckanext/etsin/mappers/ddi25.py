from functionally import first

from ..utils import get_tag_lang

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

    # Preferred identifier
    pref_id = None
    id_nos = stdy.findall('ddi:citation/ddi:titlStmt/ddi:IDNo', namespaces)
    id_no = first(filter(lambda x: x.get('agency') == 'Kansalliskirjasto', id_nos))
    if id_no is not None:
        pref_id = id_no.text

    # Title
    title = {}
    titl = stdy.findall('ddi:citation/ddi:titlStmt/ddi:titl', namespaces)
    if len(titl):
        for t in titl:
            title[get_tag_lang(t)] = t.text

    # Creator
    # Assume that 'AuthEnty' tags for different language 'citations' are in same order
    creators = []
    try:
        for i, citation in enumerate(stdy.findall('ddi:citation', namespaces)):
            for j, author in enumerate(citation.findall('ddi:rspStmt/ddi:AuthEnty', namespaces)):
                agent_obj = {'name': None}
                if 'affiliation' in author.keys():
                    org = author.get('affiliation')
                    if i == 0:
                        agent_obj['@type'] = 'Person'
                        if org is not None:
                            agent_obj['member_of'] = {
                                'name': {
                                    get_tag_lang(author): org},
                                '@type': 'Organization'}
                        agent_obj['name'] = author.text.strip()
                        creators.append(agent_obj)
                    elif org is not None:
                        creators[j]['member_of']['name'][get_tag_lang(author)] = org
                else:
                    if i == 0:
                        agent_obj['@type'] = 'Organization'
                        agent_obj['name'] = {get_tag_lang(author): author.text.strip()}
                        creators.append(agent_obj)
                    else:
                        creators[j]['name'][get_tag_lang(author)] = author.text.strip()
    except Exception as e:
        log.error('Error parsing "creators": {0}: {1}. Check that different '
                  'language elements match at the source.'.format(e.__class__.__name__, e))
        raise

    # Modified
    modified = ''
    ver_stmt = stdy.find('ddi:citation/ddi:verStmt/ddi:version', namespaces)
    if ver_stmt is not None:
        modified = ver_stmt.get('date')

    package_dict = {
        "preferred_identifier": pref_id,
        "modified": modified,
        "title": title,
        "creator": creators,
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
