# This file is part of the Etsin harvester service
#
# Copyright 2017-2018 Ministry of Education and Culture, Finland
#
# :author: CSC - IT Center for Science Ltd., Espoo Finland <servicedesk@csc.fi>
# :license: GNU Affero General Public License version 3

from ckanext.etsin.cmdi_parse_helper import CmdiParseHelper

from ..utils import get_language_identifier, convert_language, get_string_as_valid_datetime_string

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

        modified_raw = cmdi.parse_modified()
        if modified_raw:
            modified = get_string_as_valid_datetime_string(modified_raw)
        else:
            modified = None

        temporal_coverage = cmdi.parse_temporal_coverage() or None
        temporal_obj = {}
        if temporal_coverage:
            try:
                int(temporal_coverage)
                temporal_coverage_begin = get_string_as_valid_datetime_string(temporal_coverage, '01-01', '00:00:00')
                temporal_coverage_end = get_string_as_valid_datetime_string(temporal_coverage, '12-31', '23:59:59')
                if temporal_coverage_begin is None:
                    temporal_obj['temporal_coverage'] = temporal_coverage
                else:
                    temporal_obj['start_date'] = temporal_coverage_begin
                    temporal_obj['end_date'] = temporal_coverage_end
            except ValueError:
                pass

            if not temporal_obj:
                split = [item.strip() for item in temporal_coverage.split("-")]
                if len(split) == 2:
                    try:
                        temporal_coverage_begin = get_string_as_valid_datetime_string(split[0], '01-01', '00:00:00')
                        temporal_coverage_end = get_string_as_valid_datetime_string(split[1], '12-31', '23:59:59')
                        if temporal_coverage_begin is None:
                            temporal_obj['temporal_coverage'] = temporal_coverage
                        else:
                            temporal_obj['start_date'] = temporal_coverage_begin
                            temporal_obj['end_date'] = temporal_coverage_end
                    except ValueError:
                        pass
                else:
                    temporal_obj['temporal_coverage'] = temporal_coverage

        creators = cmdi.parse_creators()  # creators == owners
        # owners = cmdi.parse_owners()  # implemented but not saved to dict
        distributor = cmdi.parse_distributor()
        curators = cmdi.parse_curators()

        # TODO: licenceInfo/attributionText would suit for a custom citation
        # unless: <attributionText xml:lang="en">See Documentation section.</attributionText>
        # in which case no citation

        package_dict = {
            "title": title_list,
            "description": description_list,
            "language": language_list
        }

        if modified is not None:
            package_dict['modified'] = modified

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
