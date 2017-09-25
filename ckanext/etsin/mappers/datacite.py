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
        person = _get_person(creator)
        if not person:
            continue
        package_dict['creator'].append(person)

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
        valueURI = subject.get('valueURI')
        if subjectScheme is None and schemeURI is None:
            package_dict['keyword'].append(subject.text)
        elif subjectScheme == "YSO" or "finto.fi/yso" in schemeURI:
            if valueURI is not None:
                package_dict['theme'].append({'identifier': valueURI})
            elif is_uri(subject.text):
                package_dict['theme'].append({'identifier': subject.text})

    # Map contributor
    package_dict['contributor'] = []
    package_dict['curator'] = []
    package_dict['rights_holder'] = []
    for contributor in xml.findall('.//contributor'):
        contributorType = contributor.find('.//contributorType').text
        if contributorType in ["DataCollector", "DataCurator", "DataManager", "Editor", "Producer", "ProjectLeader", "ProjectMember", "Researcher", "ResearchGroup", "Supervisor"]:
            metaxContributorType = "contributor"
        elif contributorType == "Distributor":
            metaxContributorType = "publisher"
        elif contributorType == "ContactPerson":
            metaxContributorType = "curator"
        elif contributorType == "RightsHolder":
            metaxContributorType = "rights_holder"
        else:
            continue
        person = _get_person(contributor)
        if not Person:
            continue
        package_dict[metaxContributorType].append(person)

    # Map date
    package_dict['provenance'] = []
    for date in xml.findall('.//date'):
        dateType = date.get('dateType')
        if dateType in ['todo: find correct reference data']:  # TODO
            package_dict['provenance'].append({
                'temporal': {
                    'start_date': date.text,
                    'end_date': date.text
                },
                'type': {
                    'pref_label': dateType,
                    'identifier': 'TODO'  # TODO
                }
            })

    # Map alternate identifier
    package_dict['other_identifier'] = []
    for alternateIdentifier in xml.findall('.//alternateIdentifier'):
        alternateIdentifierType = alternateIdentifier.get(
            'alternateIdentifierType')
        if alternateIdentifierType == "URL":
            package_dict['other_identifier'].append({
                'notation': alternateIdentifier.text,
                'type': alternateIdentifierType,
            })

    # Map related identifier
    package_dict['related_entity'] = []
    for relatedIdentifier in xml.findall('.//relatedIdentifier'):
        relatedIdentifierType = relatedIdentifier.get('relatedIdentifierType')
        if relatedIdentifierType == "URL":
            relationType = relatedIdentifier.get('relationType')
            package_dict['related_entity'].append({
                "identifier": relatedIdentifier.text,
                "description": relationType,
            })

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


def _get_person(person):
    '''
    Input: LXML element that contains either DataCite creator or contributor.
    '''
    personDict = {}
    name = person.find('.//creatorName').text
    if name is not None:
        familyName = person.find('.//creatorName').get('familyName')
        givenName = person.find('.//creatorName').get('givenName')
    else:
        name = person.find('.//contributorName').text
        familyName = person.find('.//contributorName').get('familyName')
        givenName = person.find('.//contributorName').get('givenName')
    if name:
        personDict['name'] = name
    elif familyName:
        personDict['name'] = familyName
        if givenName:
            personDict['name'] += ', ' + givenName
    elif givenName:
        personDict['name'] = givenName
    else:
        return {}
    if person.find('.//nameIdentifier') is not None:
        identifier = person.find('.//nameIdentifier').text
        identifierScheme = personfind(
            './/nameIdentifier').get('nameIdentifierScheme')
        # TODO: There are some more schemes we want to map. Waiting for the
        # list.
        if identifier is not None and identifierScheme == "URL":
            personDict['identifier'] = identifier

    if person.find('.//affiliation') is not None:
        affiliation = person.find('.//affiliation').text
        if affiliation is not None:
            personDict['is_part_of'] = {
                "name": affiliation}
    return personDict
