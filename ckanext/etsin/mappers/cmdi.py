'''
Map CMDI based dicts to Metax values
'''
from ckanext.etsin.cmdi_parse_helper import CmdiParseHelper

from ..utils import get_language_identifier, convert_language

# For development use
import logging
log = logging.getLogger(__name__)

# Maps Component MetaData Infrastructure to Metax


class CmdiMetaxMapper:

    @staticmethod
    def map(xml):
        """ Convert given XML into MetaX format.
        :param xml: xml element (lxml)
        :return: dictionary
        """
        cmdi = CmdiParseHelper(xml)

        # Preferred identifier will be added in refinement
        preferred_identifier = None

        languages = cmdi.parse_languages()
        language_list = [{'title': lang,
                          'identifier': get_language_identifier(
                              convert_language(lang))}
                         for lang in languages]

        description_list = cmdi.parse_descriptions()
        title_list = cmdi.parse_titles()
        modified = cmdi.parse_modified() or ""

        temporal_coverage = cmdi.parse_temporal_coverage() or ""
        temporal_coverage_begin = ""
        temporal_coverage_end = ""
        if temporal_coverage:
            split = [item.strip() for item in temporal_coverage.split("-")]
            if len(split) == 2:
                temporal_coverage_begin = split[0]
                temporal_coverage_end = split[1]

        creators = cmdi.parse_creators()  # creators == owners
        owners = cmdi.parse_owners()  # implemented but not saved to dict
        distributor = cmdi.parse_distributor()
        curators = cmdi.parse_curators()

        metax_dict = {
            # TODO: "etsin" or such (doesn't exist yet in metax)
            "contract": "1",
            # TODO: "etsin" or such (doesn't exist yet in metax)
            "dataset_catalog": "1",
            "research_dataset": {
                "preferred_identifier": preferred_identifier,
                "creator": creators,
                "distributor": distributor,
                "modified": modified,
                "title": title_list,
                "curator": curators,
                "total_byte_size": 0,
                "description": description_list,
                "language": language_list,
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
            }
        }

        return metax_dict


def cmdi_mapper(context, data_dict):
    """ Maps a CMDI record in xml format into a MetaX format dict. """

    package_dict = data_dict['package_dict']
    xml = context.pop('xml')
    metax_dict = CmdiMetaxMapper.map(xml)
    package_dict.update(metax_dict)
    return package_dict