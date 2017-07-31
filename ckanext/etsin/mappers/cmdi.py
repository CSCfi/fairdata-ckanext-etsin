'''
Map CMDI based dicts to Metax values
'''
from functionally import first
from lxml import etree

# For development use
import logging
log = logging.getLogger(__name__)

# Maps Component MetaData Infrastructure to Metax
# TODO: Not yet implemented


def convert_language(language):
    return language     # TODO: copy from kata utils


class CmdiReaderException(Exception):
    """ Reader exception is thrown on unexpected data or error. """
    pass


class CmdiMetaxMapper:
    namespaces = {'oai': "http://www.openarchives.org/OAI/2.0/",
                  'cmd': "http://www.clarin.eu/cmd/"}

    @classmethod
    def _text_xpath(cls, root, query):
        """ Select list of texts and strip results. Use text() suffix in Xpath `query`.

        :param root: parent element (lxml) where selection is made.
        :param query: Xpath query used to get data
        :return: list of strings
        """
        return [unicode(text).strip() for text in root.xpath(query, namespaces=cls.namespaces)]

    def map(self, xml):
        """ Convert given XML into MetaX format.
        :param xml: xml element (lxml)
        :return: dictionary
        """
        cmd = first(xml.xpath('//oai:record/oai:metadata/cmd:CMD',
                              namespaces=self.namespaces))
        if cmd is None:
            raise CmdiReaderException(
                "Unexpected XML format: No CMD -element found")

        languages = self._text_xpath(
            cmd, "//cmd:corpusInfo/cmd:corpusMediaType/cmd:corpusTextInfo/cmd:languageInfo/cmd:languageId/text()")
        language_list = [{'title': lang, 'identifier': 'todo'} for lang in languages]

        description_list = []
        for desc in xml.xpath("//cmd:identificationInfo/cmd:description", namespaces=self.namespaces):
            lang = convert_language(
                desc.get('{http://www.w3.org/XML/1998/namespace}lang', 'undefined').strip())
            description_list.append({lang: unicode(desc.text).strip()})

        title_list = []
        for title in xml.xpath('//cmd:identificationInfo/cmd:resourceName', namespaces=self.namespaces):
            lang = convert_language(
                title.get('{http://www.w3.org/XML/1998/namespace}lang', 'undefined').strip())
            title_list.append({lang: title.text.strip()})

        resource_info = cmd.xpath("//cmd:Components/cmd:resourceInfo", namespaces=self.namespaces)[0]
        if resource_info is None:
            raise CmdiReaderException("Unexpected XML format: No resourceInfo -element found")

        modified = first(self._text_xpath(resource_info, "//cmd:metadataInfo/cmd:metadataLastDateUpdated/text()")) or ""

        # Note: seems like this data is not present, at least in kielipankki data
        temporal_coverage = first(self._text_xpath(resource_info, "//cmd:corpusInfo/cmd:corpusMediaType/cmd:corpusTextInfo/cmd:timeCoverageInfo/cmd:timeCoverage/text()")) or ""
        temporal_coverage_begin = ""
        temporal_coverage_end = ""
        if temporal_coverage:
            split = [item.strip() for item in temporal_coverage.split("-")]
            if len(split) == 2:
                temporal_coverage_begin = split[0]
                temporal_coverage_end = split[1]

        # things to add/use:
        # contacts
        # agents
        # identifier? (not used before) (identificationinfo//identifier)

        creator = {
            "identifier": "",
            "name": "",
            "email": "",
            "phone": ""
        }

        metax_dict = {
            # TODO: "etsin" or such (doesn't exist yet in metax)
            "contract": "1",
            # TODO: "etsin" or such (doesn't exist yet in metax)
            "dataset_catalog": "1",
            "research_dataset": {
                "creator": creator
                "modified": modified,
                "title": title_list,
                "files": [],
                "curator": [],
                "ready_status": "todo",
                "urn_identifier": "todo",
                "total_byte_size": 0,
                "description": description_list,
                "version_notes": [""],
                "language": language_list,
                "preferred_identifier": "",
                "provenance": [{
                    "temporal": [{
                        "startDate": [
                            temporal_coverage_begin
                        ],
                        "endDate": [
                            temporal_coverage_end
                        ]
                    }]
                }]
            },
            "identifier": "todo",
            "modified": "",
            "versionNotes": [
                ""
            ],
            # Pass original information to refiner
            "context": xml
        }

        return metax_dict


def cmdi_mapper(context, data_dict):

    package_dict = data_dict['package_dict']

    # TODO: figure out where xml comes from
    xml_string = context['xml']
    xml = etree.fromstring(xml_string)

    metax_dict = CmdiMetaxMapper().map(xml)
    package_dict['metax_dict'] = metax_dict

    return package_dict
