from iso639 import languages
import json


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
            return ''

def convert_language_to_6391(language):
    '''
    Convert ISO 639-2 and 639-3 language code ('fin') to ISO 639-1 ('fi'), if possible.
    Note that not all languages are included in ISO 639-1.
    '''
    try:
        part1 = languages.get(part3=language).part1
    except:
        return False

    return part1

def validate_6391(language):
    '''
    Check if language code is valid ISO 639-1.
    '''
    if not isinstance(language, basestring):
        return False

    try:
        part1 = languages.get(part1=language).part1
    except:
        return False

    return language == part1


def get_language_identifier(language):
    '''
    Returns a URI representing the given ISO 639-3 encoded language
    '''
    if not isinstance(language, basestring):
        language = 'und'

    return 'http://lexvo.org/id/iso639-3/' + language
  
def convert_to_metax_dict(data_dict, context, metax_id=None):
    '''
    :param data_dict: contains data that has come from harvester, mapped and refined
                        and about to be sent to metax
    :return: data_dict that conforms with metax json format
    '''

    import logging
    log = logging.getLogger(__name__)

    if metax_id:
        data_dict['urn_identifier'] = metax_id
    try:
        data_catalog_id = context.pop('data_catalog_id')
        # Do json dumps - loads routine to get rid of problematic character encodings
        return json.loads(json.dumps({'research_dataset': data_dict, 'data_catalog': data_catalog_id}, ensure_ascii=True))
    except Exception as e:
        log.error(e)
