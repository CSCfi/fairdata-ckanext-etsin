from functionally import first


class CmdiReaderException(Exception):
    """ Reader exception is thrown on unexpected data or error. """
    pass


class CmdiParseHelper:
    namespaces = {'oai': "http://www.openarchives.org/OAI/2.0/",
                  'cmd': "http://www.clarin.eu/cmd/"}

    def __init__(self, xml):
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
    def convert_language(cls, language):
        return language     # TODO: copy from kata utils

    def parse_languages(self):
        return self._text_xpath(
            self.cmd, "//cmd:corpusInfo/cmd:corpusMediaType/cmd:corpusTextInfo/cmd:languageInfo/cmd:languageId/text()")

    def parse_descriptions(self):
        description_list = []
        for desc in self.xml.xpath("//cmd:identificationInfo/cmd:description", namespaces=CmdiParseHelper.namespaces):
            lang = self.convert_language(
                desc.get('{http://www.w3.org/XML/1998/namespace}lang', 'undefined').strip())
            description_list.append({lang: unicode(desc.text).strip()})
        return description_list

    def parse_titles(self):
        title_list = []
        for title in self.xml.xpath('//cmd:identificationInfo/cmd:resourceName', namespaces=CmdiParseHelper.namespaces):
            lang = self.convert_language(
                title.get('{http://www.w3.org/XML/1998/namespace}lang', 'undefined').strip())
            title_list.append({lang: title.text.strip()})
        return title_list

    def parse_modified(self):
        return first(self._text_xpath(self.resource_info, "//cmd:metadataInfo/cmd:metadataLastDateUpdated/text()"))

    def parse_temporal_coverage(self):
        return first(self._text_xpath(self.resource_info, "//cmd:corpusInfo/cmd:corpusMediaType/cmd:corpusTextInfo/cmd:timeCoverageInfo/cmd:timeCoverage/text()"))

    def parse_licence(self):
        return first(self._text_xpath(
            self.resource_info, "//cmd:distributionInfo/cmd:licenceInfo/cmd:licence/text()"))
