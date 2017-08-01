'''
Map CMDI based dicts to Metax values
'''
from lxml import etree
from ckanext.etsin.cmdi_parse_helper import CmdiParseHelper

# For development use
import logging
log = logging.getLogger(__name__)

# Maps Component MetaData Infrastructure to Metax
# TODO: Not yet implemented


class CmdiMetaxMapper:

    def map(self, xml):
        """ Convert given XML into MetaX format.
        :param xml: xml element (lxml)
        :return: dictionary
        """
        helper = CmdiParseHelper(xml)

        languages = helper.parse_languages()
        language_list = [{'title': lang, 'identifier': 'todo'} for lang in languages]

        description_list = helper.parse_descriptions()
        title_list = helper.parse_titles()
        modified = helper.parse_modified() or ""

        temporal_coverage = helper.parse_temporal_coverage() or ""
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
                "creator": creator,
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
