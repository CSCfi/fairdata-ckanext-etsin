from functionally import first
from pylons import config
import ckanext.etsin.utils


class CmdiReaderException(Exception):
    """ Reader exception is thrown on unexpected data or error. """
    pass


class CmdiParseHelper:
    namespaces = {'oai': "http://www.openarchives.org/OAI/2.0/",
                  'cmd': "http://www.clarin.eu/cmd/"}

    def __init__(self, xml, provider=None):
        """ Initialize the helper for parsing the given xml.

        :param xml: an lxml object, representing a CMDI record
        """
        cmd = first(xml.xpath('//oai:record/oai:metadata/cmd:CMD',
                              namespaces=CmdiParseHelper.namespaces))
        if cmd is None:
            raise CmdiReaderException(
                "Unexpected XML format: No CMD -element found")

        resource_info = cmd.xpath(
            "//cmd:Components/cmd:resourceInfo", namespaces=CmdiParseHelper.namespaces)[0]
        if resource_info is None:
            raise CmdiReaderException(
                "Unexpected XML format: No resourceInfo -element found")

        self.xml = xml
        self.cmd = cmd
        self.resource_info = resource_info
        self.provider = provider or config.get('ckan.site_url')

    @staticmethod
    def _strip_first(elements):
        """ Strip and return first element.

        :param elements: list of xml elements
        :return: first element or none
        """
        return (first(elements) or "").strip()

    @classmethod
    def _text_xpath(cls, root, query):
        """ Select list of texts and strip results. Use text() suffix in Xpath `query`.

        :param root: parent element (lxml) where selection is made.
        :param query: Xpath query used to get data
        :return: list of strings
        """
        return [unicode(text).strip() for text in root.xpath(query, namespaces=cls.namespaces)]

    @classmethod
    def _get_organizations(cls, root, xpath):
        """ Extract organization dictionaries from XML using given Xpath.

        :param root: parent element (lxml) where selection is done.
        :param xpath: xpath selector used to get data
        :return: list of organization dictionaries
        """
        return [{'role': cls._strip_first(organization.xpath("cmd:role/text()", namespaces=cls.namespaces)),
                 'name': ", ".join(cls._text_xpath(organization, "cmd:organizationInfo/cmd:organizationName/text()")),
                 'short_name': cls._strip_first(organization.xpath("cmd:organizationInfo/cmd:organizationShortName/text()", namespaces=cls.namespaces)),
                 'email': cls._strip_first(organization.xpath("cmd:organizationInfo/cmd:communicationInfo/cmd:email/text()", namespaces=cls.namespaces)),
                 'url': cls._strip_first(organization.xpath("cmd:organizationInfo/cmd:communicationInfo/cmd:email/text()", namespaces=cls.namespaces))}

                for organization in root.xpath(xpath, namespaces=cls.namespaces)]

    @classmethod
    def _get_persons(cls, root, xpath):
        """ Extract person dictionary from XML using given Xpath.

        :param root: parent element (lxml) where selection is done
        :param xpath: xpath selector used to get data
        :return: list of person dictionaries
        """
        return [{'role': cls._strip_first(person.xpath("cmd:role/text()", namespaces=cls.namespaces)),
                 'surname': cls._strip_first(person.xpath("cmd:personInfo/cmd:surname/text()", namespaces=cls.namespaces)),
                 'given_name': cls._strip_first(person.xpath("cmd:personInfo/cmd:givenName/text()", namespaces=cls.namespaces)),
                 'email': cls._strip_first(person.xpath("cmd:personInfo/cmd:communicationInfo/cmd:email/text()", namespaces=cls.namespaces)),
                 'organization': first(cls._get_organizations(person, "cmd:personInfo/cmd:affiliation"))}
                for person in root.xpath(xpath, namespaces=cls.namespaces)]

    @staticmethod
    def _get_person_as_agent(person):
        """ Converts a person dictionary to MetaX agent format.

        :param person: dictionary produced by the _get_persons method
        :return: dictionary in the MetaX agent format
        """
        return {
            "identifier": "todo",
            "name": u"{} {}".format(person['given_name'], person['surname']),
            "email": person['email'],
            "phone": "todo",
            "isPartOf": person['organization']
        }

    @staticmethod
    def _get_organization_as_agent(organization):
        """ Converts an organization dictionary to MetaX agent format.

        :param organization: dictionary produced by the _get_organizations method
        :return: dictionary in the MetaX agent format
        """
        return {
            "identifier": "todo",
            "name": organization['name'],
            "email": organization['email'],
        }

    def parse_languages(self):
        """ Find languages as defined in language info

        :return: list of languages
        """
        return self._text_xpath(
            self.cmd, "//cmd:corpusInfo/cmd:corpusMediaType/cmd:corpusTextInfo/cmd:languageInfo/cmd:languageId/text()")

    def parse_descriptions(self):
        """ Find descriptions in each language

        :return: list of dictionaries of format { language: description }
        """
        description_list = []
        for desc in self.xml.xpath("//cmd:identificationInfo/cmd:description", namespaces=CmdiParseHelper.namespaces):
            lang = utils.convert_language(
                desc.get('{http://www.w3.org/XML/1998/namespace}lang', 'undefined').strip())
            description_list.append({lang: unicode(desc.text).strip()})
        return description_list

    def parse_titles(self):
        """ Find titles in each language

        :return: list of dictionaries of format { language: title }
        """
        title_list = []
        for title in self.xml.xpath('//cmd:identificationInfo/cmd:resourceName', namespaces=CmdiParseHelper.namespaces):
            lang = self.convert_language(
                title.get('{http://www.w3.org/XML/1998/namespace}lang', 'undefined').strip())
            title_list.append({lang: title.text.strip()})
        return title_list

    def parse_modified(self):
        """ Find date when metadata was last modified """
        return first(self._text_xpath(self.resource_info, "//cmd:metadataInfo/cmd:metadataLastDateUpdated/text()"))

    def parse_temporal_coverage(self):
        """ Find time coverage of the metadata """
        return first(self._text_xpath(self.resource_info, "//cmd:corpusInfo/cmd:corpusMediaType/cmd:corpusTextInfo/cmd:timeCoverageInfo/cmd:timeCoverage/text()"))

    def parse_licence(self):
        """ Find the license for the metadata """
        return first(self._text_xpath(
            self.resource_info, "//cmd:distributionInfo/cmd:licenceInfo/cmd:licence/text()"))

    def parse_distributors(self):
        """ Get a list of the distribution right holders (people or organizations) as agents. """
        return [
            self._get_person_as_agent(person) for person in self._get_persons(self.resource_info, "//cmd:distributionInfo/cmd:licenceInfo/cmd:distributionRightsHolderPerson")
        ].extend([
            self._get_organization_as_agent(organization) for organization in self._get_organizations(self.resource_info, "//cmd:distributionInfo/cmd:licenceInfo/cmd:distributionRightsHolderOrganization")
        ])

    def parse_creators(self):
        return []   # TODO

    def parse_owners(self):
        """ Get a list of the owners (people or organizations) as agents. """
        creator_persons = self._get_persons(
            self.resource_info, "//cmd:distributionInfo/cmd:iprHolderPerson")
        creator_organizations = self._get_organizations(
            self.resource_info, "//cmd:distributionInfo/cmd:iprHolderOrganization")
        return [
            self._get_person_as_agent(person) for person in creator_persons
        ].extend([
            self._get_organization_as_agent(organization) for organization in creator_organizations
        ])

    def parse_curators(self):
        """ Get the curators (contacts) as agents. Curators may be people or organizations. """
        contact_persons = self._get_persons(
            self.resource_info, "//cmd:contactPerson")
        return [self._get_person_as_agent(person) for person in contact_persons]

    def parse_metadata_identifiers(self):
        """ Get the metadata identifiers. """
        return self._text_xpath(
            self.cmd, "//cmd:identificationInfo/cmd:identifier/text()")
