'''
Map Datacite 3.1 and 4.0 dicts to Metax values
'''

from lxml import objectify

from ..utils import validate_6391, get_language_identifier, is_uri

import logging
log = logging.getLogger(__name__)

# Mapper receives an LXML element and maps it to Metax format


def datacite_mapper(xml):

    from lxml import etree

    # Strip element prefixes
    xml = _strip_prefixes(xml)

    # Start with an empty slate
    package_dict = {}

    # Map identifier
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

    # Map creators
    package_dict['creator'] = []
    for creator in xml.findall('.//creator'):
        metaxCreator = {}

        creatorName = creator.find('.//creatorName').text
        creatorFamilyName = creator.find('.//creatorName').get('familyName')
        creatorGivenName = creator.find('.//creatorName').get('givenName')
        if creatorName is not None:
            metaxCreator['name'] = creatorName
        elif creatorFamilyName is not None:
            metaxCreator['name'] = creatorFamilyName
            if creatorGivenName is not None:
                metaxCreator['name'] += ", " + creatorGivenName
        elif creatorGivenName is not None:
            metaxCreator['name'] = creatorGivenName
        else:  # Skip creator with no name
            continue

        if creator.find('.//nameIdentifier') is not None:
            creatorIdentifier = creator.find('.//nameIdentifier').text
            creatorIdentifierScheme = creator.find(
                './/nameIdentifier').get('nameIdentifierScheme')
            # TODO: There are some more schemes we want to map. Waiting for the
            # list.
            if creatorIdentifier is not None and creatorIdentifierScheme == "URL":
                metaxCreator['identifier'] = creatorIdentifier

        if creator.find('.//affiliation') is not None:
            creatorAffiliation = creator.find('.//affiliation').text
            if creatorAffiliation is not None:
                metaxCreator['is_part_of'] = {"name": creatorAffiliation}

        package_dict['creator'].append(metaxCreator)

    # Map language
    language = xml.find('.//identifier')
    if language is not None:
        # Language should be either ISO 639-1 or IETF BCP 47. The first two
        # characters of IETF BCP 47 should be same as ISO 639-1 code.
        if validate_6391(language[0:2]):
            language = get_language_identifier(language[0:2])
            package_dict['language'] = language
        else:
            language = "default"
    else:
        # Use "default" for title and description language codes, but don't
        # save it in language field
        language = "default"

    # Map title
    # In case of multiple primary titles, pick only the first one
    for title in xml.findall('.//title'):
        titleType = xml.find('.//title').get('titleType')
        if not titleType:
            # Title is primary when there's no titleType
            package_dict['title'] = [{language: title.text}]
            break

    # Map publisher
    publisher = xml.find('.//publisher').text
    package_dict['publisher'] = [{'name': publisher}]

    # Map publication year
    publication_year = xml.find('.//publicationYear').text
    package_dict['issued'] = publication_year

    # Map subject
    package_dict['keyword'] = []
    package_dict['theme'] = []
    for subject in xml.findall('.//subject'):
        subjectScheme = subject.get('subjectScheme')
        schemeURI = subject.get('schemeURI')
        if subjectScheme is None and schemeURI is None:
            package_dict['keyword'].append(subject.text)
        elif subjectScheme == "YSO" or "finto.fi/yso" in schemeURI:
            if is_uri(subject.text):
                package_dict['theme'].append({'identifier': subject.text})

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
