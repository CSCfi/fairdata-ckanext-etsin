import json
import logging
import csv

from iso639 import languages

log = logging.getLogger(__name__)


def convert_language(language):
    '''
    Convert alpha2 language (eg. 'en') to terminology language (eg. 'eng')
    '''

    if not language:
        return "und"

    try:
        lang_object = languages.get(part1=language)
        return lang_object.terminology
    except KeyError as ke:
        try:
            lang_object = languages.get(part2b=language)
            return lang_object.terminology
        except KeyError as ke:
            log.error('KeyError: key not found: {0}'.format(ke.args))
            return ''

def convert_language_to_6391(language):
    '''
    Convert ISO 639-2 and 639-3 language code ('fin') to ISO 639-1 ('fi'), if possible.
    Note that not all languages are included in ISO 639-1.
    '''
    return languages.get(part3=language).part1


def get_language_identifier(lang):
    '''
    Returns a URI representing the given ISO 639-3 encoded language
    '''
    if not isinstance(lang, basestring):
        lang = 'und'

    return 'http://lexvo.org/id/iso639-3/' + lang


def convert_to_metax_dict(data_dict, context, metax_id=None):
    '''
    :param data_dict: contains data that has come from harvester, mapped and refined
                        and about to be sent to metax
    :return: data_dict that conforms with metax json format
    '''

    if metax_id:
        data_dict['urn_identifier'] = metax_id
    try:
        data_catalog_id = context.pop('data_catalog_id')
        # Do json dumps - loads routine to get rid of problematic character encodings
        return json.loads(json.dumps({'research_dataset': data_dict, 'data_catalog': data_catalog_id}, ensure_ascii=True))
    except KeyError as ke:
        log.error('KeyError: key not found: {0}'.format(ke.args))
    except Exception as e:
        log.error(e)


def convert_bbox_to_polygon(north, east, south, west):
    return 'POLYGON(({s} {w},{s} {e},{n} {e},{n} {w},{s} {w}))'.format(n=north, e=east, s=south, w=west)


def set_existing_kata_identifier_to_other_identifier(file_path, search_pid, package_dict):
    package_dict['other_identifier'] = []
    with open(file_path, 'rb') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if row[0] == search_pid:
                package_dict['other_identifier'].append({
                    'notation': row[1],
                    'type': {
                         'identifier': 'http://purl.org/att/es/reference_data/identifier_type/identifier_type_urn'
                    }
                })
