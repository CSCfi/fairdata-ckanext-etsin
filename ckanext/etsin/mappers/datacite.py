'''
Map Datacite 3.1 and 4.0 dicts to Metax values
'''

from lxml import objectify

# from iso639 import languages
# from ..utils import get_language_identifier, convert_language_to_6391

import logging
log = logging.getLogger(__name__)

# Mapper receives an LXML element and maps it to Metax format


def datacite_mapper(xml):

    from lxml import etree

    # Strip element prefixes
    xml = _strip_prefixes(xml)

    # Start with an empty slate
    package_dict = {}

    # Identifier to preferred_identifier
    # According to DataCite 4.0 schema, IdentifierType should always be "DOI", 
    # but OpenAire seems to use URLs as well
    identifier = xml.find('.//identifier')
    identifier_type = xml.find('.//identifier').get('identifierType')
    if identifier_type == "URL":
        package_dict['preferred_identifier'] = identifier.text
    elif identifier_type == "DOI":
        package_dict['preferred_identifier'] = "https://dx.doi.org/" + \
            identifier.text
    else:
        package_dict['preferred_identifier'] = ""

    # # Creator name to agent
    # # TODO: map nameIdentifier to agent.id and nameIdentifierScheme and schemeURI
    # # to extras
    # agents = []
    # for creator in xml.findall('.//{http://datacite.org/schema/kernel-3}creator'):
    #     creatorName = creator.find('.//{http://datacite.org/schema/kernel-3}creatorName').text
    #     creatorAffiliation = creator.find('.//{http://datacite.org/schema/kernel-3}affiliation').text
    #     agents.append({
    #         'role': u'author',
    #         'name': creatorName,
    #         'organisation': creatorAffiliation
    #         })

    # # Primary title to title
    # # TODO: if titleType is present, check to find out if title is actually primary
    # # TODO: map non-primary titles to extras
    # title = xml.find('.//{http://datacite.org/schema/kernel-3}title').text
    # langtitle = [{'lang': 'en', 'value': title}] # Assuming we always
    # harvest English

    # # Publisher to contact
    # publisher = xml.find('.//{http://datacite.org/schema/kernel-3}publisher').text
    # contacts = [{'name': publisher}]

    # # Publication year to event
    # publication_year = xml.find('.//{http://datacite.org/schema/kernel-3}publicationYear').text
    # events = [{'type': u'published', 'when': publication_year, 'who':
    # publisher, 'descr': u'Dataset was published'}]

    # # MAP DATACITE RECOMMENDED FIELDS

    # # Subject to tags
    # # TODO: map subjectsScheme and schemeURI to extras

    # # Contributor to agent
    # # TODO: map nameIdentifier to agent.id, nameIdentifierScheme, schemeURI and
    # # contributorType to extras
    # for contributor in xml.findall('.//{http://datacite.org/schema/kernel-3}contributor'):
    #     contributorName = contributor.find('.//{http://datacite.org/schema/kernel-3}contributorName').text
    #     contributorAffiliation = contributor.find('.//{http://datacite.org/schema/kernel-3}affiliation').text
    #     agents.append({
    #         'role': u'contributor',
    #         'name': contributorName,
    #         'organisation': contributorAffiliation
    #         })

    # # Date to event
    # for date in xml.findall('.//{http://datacite.org/schema/kernel-3}date'):
    #     events.append({
    #       'type': date.get('dateType'),
    #       'when': date.text,
    #       'who': u'unknown',
    #       'descr': date.get('dateType'),
    #       })

    # # ResourceType to extra
    # # TODO: map resourceType and resourceTypeGeneral to extras

    # # RelatedIdentifier to showcase
    # # TODO: map RelatedIdentifier to showcase title, relatedIdentifierType, relationType,
    # # relatedMetadataScheme, schemeURI and schemeType to showcase description

    # # Description to langnotes
    # description = ''
    # for element in xml.findall('.//{http://datacite.org/schema/kernel-3}description'):
    #     description += element.get('descriptionType') + ': ' + element.text + ' '
    # langnotes = [{
    #   'lang': 'en', # Assuming we always harvest English
    #   'value': description,
    #   }]

    # # GeoLocation to geograhic_coverage
    # # TODO: map geoLocationPoint and geoLocationBox to extras, geoLocationPlace to
    # # geographic_coverage

    # # MAP DATACITE OPTIONAL FIELDS

    # # Language to language
    # # TODO: map language to language

    # # AlternateIdentifier to pids
    # # TODO: map AlternateIdentifier to pids.id, alternateIdentifierType to pids.provider

    # # Size to extra
    # # TODO: map size to extra

    # # Format to resources
    # # TODO: map format to resources.format

    # # Version to extra
    # # DataCite version is a string such as 'v3.2.1' and can't be used as Etsin version
    # # TODO: map version to extra

    # # Rights to license
    # # license_URL = ''
    # for right in xml.findall('.//{http://datacite.org/schema/kernel-3}rights'):
    #     license_URL += right.text + ' ' + right.get('rightsURI') + ' '

    return {
        "research_dataset": package_dict}


def _strip_prefixes(xml):
    root = xml.getroottree()

    # Zenodo uses {namespace}element
    for elem in root.getiterator():
        if not hasattr(elem.tag, 'find'):  # pass comments
            continue

        i = elem.tag.find('}')
        if i >= 0:
            elem.tag = elem.tag[i + 1:]

    # OpenAire uses namespace:element
    objectify.deannotate(root, cleanup_namespaces=True)

    return xml
