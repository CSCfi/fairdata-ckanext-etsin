'''
Map Datacite 3.1 and 4.0 xml to Metax values
'''

# NOTE: This mapper should be fixed to work with the data model. Currently would break.

from lxml import objectify

from ..metax_api import get_ref_data
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
            language = "und"
    else:
        # Use "und" for title and description language codes, but don't
        # save it in language field
        language = "und"

    # Map title
    # In case of multiple primary titles, pick only the first one
    for title in xml.findall('.//title'):
        title_type = xml.find('.//title').get('titleType')
        if not title_type:
            # Title is primary when there's no titleType
            package_dict['title'] = {language: title.text}
            break

    # Map publisher
    publisher = xml.find('.//publisher').text
    package_dict['publisher'] = []
    if publisher:
        package_dict['publisher'].append({'name': publisher})

    # Map publication year
    publication_year = xml.find('.//publicationYear').text
    package_dict['issued'] = publication_year

    # Map subject
    package_dict['keyword'] = []
    package_dict['theme'] = []
    for subject in xml.findall('.//subject'):
        subject_scheme = subject.get('subjectScheme')
        scheme_URI = subject.get('schemeURI')
        value_URI = subject.get('valueURI')
        if subject_scheme is None and scheme_URI is None:
            package_dict['keyword'].append(subject.text)
        elif subject_scheme == "YSO" or "finto.fi/yso" in scheme_URI:
            if value_URI is not None:
                package_dict['theme'].append({'identifier': value_URI})
            elif is_uri(subject.text):
                package_dict['theme'].append({'identifier': subject.text})

    # Map contributor
    package_dict['contributor'] = []
    package_dict['curator'] = []
    package_dict['rights_holder'] = []
    for contributor in xml.findall('.//contributor'):
        contributor_type = contributor.find('.//contributorType').text
        if contributor_type in ["DataCollector", "DataCurator", "DataManager", "Editor", "Producer", "ProjectLeader", "ProjectMember", "Researcher", "ResearchGroup", "Supervisor"]:
            metax_contributor_type = "contributor"
        elif contributor_type == "Distributor":
            metax_contributor_type = "publisher"
        elif contributor_type == "ContactPerson":
            metax_contributor_type = "curator"
        elif contributor_type == "RightsHolder":
            metax_contributor_type = "rights_holder"
        else:
            continue
        person = _get_person(contributor)
        if not person:
            continue
        package_dict[metax_contributor_type].append(person)

    if len(package_dict['publisher']) == 0:
        del package_dict['publisher']

    if len(package_dict['contributor']) == 0:
        del package_dict['contributor']

    if len(package_dict['curator']) == 0:
        del package_dict['curator']

    if len(package_dict['rights_holder']) == 0:
        del package_dict['rights_holder']

    # Map date
    package_dict['provenance'] = []
    for date in xml.findall('.//date'):
        date_type = date.get('dateType')
        if date_type in ['todo: find correct reference data']:  # TODO
            package_dict['provenance'].append({
                'temporal': {
                    'start_date': date.text,
                    'end_date': date.text
                }
            })

    # Map alternate identifier
    package_dict['other_identifier'] = []
    for alternate_identifier in xml.findall('.//alternateIdentifier'):
        alternate_identifier_type = alternate_identifier.get(
            'alternateIdentifierType')
        if alternate_identifier_type == "URL":
            package_dict['other_identifier'].append({
                'notation': alternate_identifier.text,
                'type': alternate_identifier_type,
            })

    # Map related identifier
    package_dict['related_entity'] = []
    for related_identifier in xml.findall('.//relatedIdentifier'):
        related_identifier_type = related_identifier.get('relatedIdentifierType')
        if related_identifier_type == "URL":
            relation_type = related_identifier.get('relationType')
            package_dict['related_entity'].append({
                "identifier": related_identifier.text,
                "description": relation_type,
            })

    # Map version
    version = xml.find('.//publicationYear')
    if version is not None:
        package_dict['version_info'] = version.text

    # Map rights
    package_dict['access_rights'] = []
    for right in xml.findall('.//rights'):
        rights_URI = right.get('rightsURI')

        # Query reference data for identifier matching this URI
        rights_identifier = get_ref_data('license', 'uri', rights_URI, 'id')
        if rights_identifier is not None:
            package_dict['access_rights'].append({
                'description': right.text,
                'license': {'identifier': rights_identifier},
            })
        else:
            package_dict['access_rights'].append({
                'description': right.text
            })

    # Map description
    full_description = ""
    for description in xml.findall('.//description'):
        full_description += description.get('descriptionType') + \
            ': ' + description.text + ' '
    package_dict['description'] = [{language: full_description}]

    # Map geolocation
    package_dict['location'] = []
    for location in xml.findall('.//geoLocation'):
        point = location.find('.//geoLocationPoint')
        if point is not None:
            longitude = point.find('.//pointLongitude').text
            latitude = point.find('.//pointLatitude').text
            package_dict['location'].append({
                "as_wkt": "POINT (" + pointLongitude + " " + pointLatitude + ")"})
        box = location.find('.//geoLocationBox')
        if box is not None:
            west = point.find('.//westBoundLongitude').text
            east = point.find('.//eastBoundLongitude').text
            north = point.find('.//northBoundLatitude').text
            south = point.find('.//soundBoundLatitude').text
            package_dict['location'].append({
                "as_wkt": "POLYGON ((" + west + " " + south + ", " + west + " " + north + ", " + east + " " + north + ", " + east + " " + south + ", " + west + " " + south + "))"})
        place = location.find('.//geoLocationPlace')
        if place is not None:
            package_dict['location'].append({"geographic_name": place.text})
        polygon = location.find('.//geoLocationPolygon')
        if polygon is not None:
            polygon_string = "POLYGON (("
            for point in xml.findall('.//polygonPoint'):
                longitude = point.find('.//pointLongitude').text
                latitude = point.find('.//pointLatitude').text
                polygon_string += longitude + " " + latitude + ", "
            polygon_string[-2:] = "))"  # replace last ", "

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
    person_dict = {'@type': 'Person'}
    name = person.find('.//creatorName')
    if name is None:
        name = person.find('.//contributorName')
    family_name = name.get('familyName')
    given_name = name.get('givenName')
    if name is not None and name.text:
        person_dict['name'] = name.text
    elif family_name:
        person_dict['name'] = family_name
        if given_name:
            person_dict['name'] += ', ' + given_name
    elif given_name:
        person_dict['name'] = given_name
    else:
        return {}
    if person.find('.//nameIdentifier') is not None:
        identifier = person.find('.//nameIdentifier')
        identifier_scheme = identifier.get('nameIdentifierScheme')
        # TODO: There are some more schemes we want to map. Waiting for the
        # list.
        if identifier is not None and identifier_scheme == "URL":
            person_dict['identifier'] = identifier.text

    if person.find('.//affiliation') is not None:
        affiliation = person.find('.//affiliation').text
        if affiliation is not None:
            person_dict['member_of'] = {
                "@type": 'Organization',
                "name": {"und": affiliation}
            }
    return person_dict
