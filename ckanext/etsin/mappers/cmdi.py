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
        cmd = first(xml.xpath('//oai:record/oai:metadata/cmd:CMD',
                              namespaces=self.namespaces))
        if cmd is None:
            raise CmdiReaderException(
                "Unexpected XML format: No CMD -element found")

        resource_info = cmd.xpath(
            "//cmd:Components/cmd:resourceInfo", namespaces=self.namespaces)[0]
        if resource_info is None:
            raise CmdiReaderException(
                "Unexpected XML format: No resourceInfo -element found")

        metadata_identifiers = self._text_xpath(
            cmd, "//cmd:identificationInfo/cmd:identifier/text()")

        languages = self._text_xpath(
            cmd, "//cmd:corpusInfo/cmd:corpusMediaType/cmd:corpusTextInfo/cmd:languageInfo/cmd:languageId/text()")

        # convert the descriptions to a JSON string of type {"fin":"kuvaus", "eng","desc"}
        description = []
        for desc in xml.xpath("//cmd:identificationInfo/cmd:description", namespaces=self.namespaces):
            lang = convert_language(
                desc.get('{http://www.w3.org/XML/1998/namespace}lang', 'undefined').strip())
            description.append({lang: unicode(desc.text).strip()})

        # convert the titles to a JSON string of type {"fin":"otsikko", "eng","title"}
        title = []
        for title in xml.xpath('//cmd:identificationInfo/cmd:resourceName', namespaces=self.namespaces):
            lang = convert_language(
                title.get('{http://www.w3.org/XML/1998/namespace}lang', 'undefined').strip())
            title.append({lang: title.text.strip()})

        metax_dict = {
            # TODO: "etsin" or such (doesn't exist yet in metax)
            "contract": "1",
            # TODO: "etsin" or such (doesn't exist yet in metax)
            "dataset_catalog": "1",
            "research_dataset": {
                "creator": "metadatacreator?",
                "modified": "lastdateupdate",
                "title": title,
                "files": [],    # ?
                "curator": [],  # ?
                "ready_status": "",     # ?
                "urn_identifier": "",
                "total_byte_size": 0,
                "description": description,
                "version_notes": [""],
                "language": [],
                "preferred_identifier": ""
            },
            "identifier": "header.id or idinfo.id",
            "modified": "",
            "versionNotes": [
                ""
            ]
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
