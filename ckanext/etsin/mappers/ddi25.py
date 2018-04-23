# coding=UTF8
from functionally import first

from ..metax_api import get_ref_data
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

    # Description
    description = [{}]
    try:
        for abstract in stdy.findall('ddi:stdyInfo/ddi:abstract', namespaces):
            description[0][get_tag_lang(abstract)] = unicode(abstract.text).strip()
    except Exception as e:
        log.error('Error parsing "description": {0}: {1}'.format(e.__class__.__name__, e))
        raise

    # Keywords
    keywords = []
    for kw in stdy.findall('ddi:stdyInfo/ddi:subject/ddi:keyword', namespaces):
        keywords.append(kw.text.strip())
    vocab = 'CESSDA Topic Classification'
    for cterm in stdy.findall("ddi:stdyInfo/ddi:subject/ddi:topcClas[@vocab='{0}']".format(vocab), namespaces):
        keywords.append(cterm.text.strip())

    # Field of science
    codes = set()
    for fos in stdy.findall("ddi:stdyInfo/ddi:subject/ddi:topcClas[@vocab='OKM']", namespaces):
        field = 'label.' + get_tag_lang(fos)
        codes.add(get_ref_data('field_of_science', field, fos.text.strip(), 'code'))
    field_of_science = [{'identifier': c} for c in codes ]
    if not len(field_of_science):
        log.debug("No 'field of science' found.")
        field_of_science.append({'identifier': 'ta5',
                                 'definition': [{'en': 'Fallback field of science'}]})

    # Publisher
    publisher = {
                    'name': {},
                    '@type': 'Organization',
                    "homepage": {
                        "title": {
                            "en": "Publisher website",
                            "fi": "Julkaisijan kotisivu"},
                        "identifier": ""}
    }
    for dist in stdy.findall('ddi:citation/ddi:distStmt', namespaces):
        distr = dist.find('ddi:distrbtr', namespaces)
        publisher['name'][get_tag_lang(distr)] = distr.text.strip()
        publisher['homepage']['identifier'] = distr.get('URI')

    # Temporal coverage
    tpath = "ddi:stdyInfo/ddi:sumDscr/ddi:{tag}[@event='{ev}']"
    tstart = stdy.find(tpath.format(tag='timePrd', ev='start'), namespaces) or\
        stdy.find(tpath.format(tag='collDate', ev='start'), namespaces)
    tend = stdy.find(tpath.format(tag='timePrd', ev='end'), namespaces) or\
        stdy.find(tpath.format(tag='collDate', ev='end'), namespaces)
    if tstart is None and tend is None:
        tstart = stdy.find(tpath.format(tag='timePrd', ev='single'), namespaces) or\
                 stdy.find(tpath.format(tag='collDate', ev='single'), namespaces)
        tend = tstart
    elif tstart is None or tend is None:
        log.error('No temporal coverage or only start or end date in dataset!')
    temporal_coverage = [{'start_date': tstart.get('date') if tstart is not None else '',
                          'end_date': tend.get('date') if tend is not None else ''}]

    # Provenance
    provenance = [{'title': {'en': 'Collection'},
                   'temporal': temporal_coverage[0],
                   'description': {
                       'en': 'Contains the date(s) when the data were collected.'}
                   }]
    # Production
    prod = stdy.find('ddi:citation/ddi:prodStmt/ddi:prodDate', namespaces)
    if prod is not None:
        provenance.append(
            {'title': {'en': 'Production'},
             'temporal': {'start_date': prod.text.strip(),
                          'end_date': prod.text.strip()},
             'description': {'en': 'Date when the data collection were'
                                   ' produced (not distributed or archived)'}})

    # Geographical coverage
    spatial = [{}]
    lang_attr = '{http://www.w3.org/XML/1998/namespace}lang'
    lang_path = "ddi:stdyInfo/ddi:sumDscr/ddi:nation[@{la}='{lt}']"
    nat_fi = stdy.find(lang_path.format(la=lang_attr, lt='fi'), namespaces)
    nat_en = stdy.find(lang_path.format(la=lang_attr, lt='en'), namespaces)
    if nat_en is not None:
        spatial = [{'geographic_name': nat_en.text.strip()}]
    if nat_fi is not None:
        # Assume Finland so search ES for Finnish place names: 'nat_fi'
        spat_id = get_ref_data('location', 'label.fi', nat_fi.text.strip(),
                               'code')
        if spat_id is not None:
            spatial[0]['place_uri'] = {'identifier': spat_id}
        if spatial[0].get('geographic_name') is None:
            spatial[0]['geographic_name'] = nat_fi.text.strip()

    package_dict = {
        "preferred_identifier": pref_id,
        "modified": modified,
        "title": title,
        "creator": creators,
        "description": description,
        "keywords": keywords,
        "field_of_science": field_of_science,
        "publisher": publisher,
        "temporal": temporal_coverage,
        "provenance": provenance,
        "spatial": spatial
    }

    return package_dict
