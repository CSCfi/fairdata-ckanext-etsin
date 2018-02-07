'''
Map CMDI based xml to Metax values
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
        language_list = [{'identifier': get_language_identifier(convert_language(lang))} for lang in languages]

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

        package_dict = {
            "preferred_identifier": preferred_identifier,
            "modified": modified,
            "title": title_list,
            "description": description_list,
            "language": language_list,
            "provenance": [{
                "temporal": {
                    "startDate": temporal_coverage_begin,
                    "endDate": temporal_coverage_end
                }
            }],
            "access_rights": {
                "available": "TODO: metadataCreationDate?",
                "description": [{
                    "en": "TODO: Free account of the rights. This could be licenceInfo/attributionText"}],
            }
        }

        if distributor:
            package_dict.update({"publisher": distributor})

        if creators:
            package_dict.update({"creator": creators})

        if curators:
            package_dict.update({"curator": curators})

        return package_dict


def cmdi_mapper(xml):
    """ Maps a CMDI record in xml format into a MetaX format dict. """
    return CmdiMetaxMapper.map(xml)
