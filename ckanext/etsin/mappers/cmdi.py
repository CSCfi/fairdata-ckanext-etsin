# This file is part of the Etsin harvester service
#
# Copyright 2017-2018 Ministry of Education and Culture, Finland
#
# :author: CSC - IT Center for Science Ltd., Espoo Finland <servicedesk@csc.fi>
# :license: GNU Affero General Public License version 3

from ckanext.etsin.cmdi_parse_helper import CmdiParseHelper

from ..utils import get_language_identifier, convert_language

# For development use
import logging
log = logging.getLogger(__name__)


class CmdiMetaxMapper:
    '''
    Map Component MetaData Infrastructure (CMDI) based xml to Metax values
    '''
    @staticmethod
    def map(xml):
        """ Convert given XML into MetaX format.
        :param xml: xml element (lxml)
        :return: dictionary
        """
        cmdi = CmdiParseHelper(xml)

        languages = cmdi.parse_dataset_languages()
        language_list = [{'identifier': get_language_identifier(convert_language(lang))} for lang in languages]

        description_list = cmdi.parse_descriptions()
        title_list = cmdi.parse_titles()
        modified = cmdi.parse_modified() or ""

        temporal_coverage = cmdi.parse_temporal_coverage() or None
        temporal_coverage_begin = ''
        temporal_coverage_end = ''
        if temporal_coverage:
            try:
                temporal_coverage_begin = str(int(temporal_coverage))
                temporal_coverage_end = str(int(temporal_coverage))
            except ValueError:
                pass

            if not temporal_coverage_begin:
                split = [item.strip() for item in temporal_coverage.split("-")]
                if len(split) == 2:
                    try:
                        temporal_coverage_begin = split[0]
                        temporal_coverage_end = split[1]
                    except ValueError:
                        pass

        creators = cmdi.parse_creators()  # creators == owners
        # owners = cmdi.parse_owners()  # implemented but not saved to dict
        distributor = cmdi.parse_distributor()
        curators = cmdi.parse_curators()

        # TODO: licenceInfo/attributionText would suit for a custom citation
        # unless: <attributionText xml:lang="en">See Documentation section.</attributionText>
        # in which case no citation

        package_dict = {
            "modified": modified,
            "title": title_list,
            "description": description_list,
            "language": language_list
        }

        temporal_obj = {}
        if temporal_coverage_begin:
            temporal_obj.update({"start_date": temporal_coverage_begin})

        if temporal_coverage_end:
            temporal_obj.update({"end_date": temporal_coverage_end})

        if temporal_obj:
            package_dict.update({"temporal": [temporal_obj]})

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
