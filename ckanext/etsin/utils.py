from iso639 import languages


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


def convert_to_metax_dict(data_dict):
    '''
    :param data_dict: contains data that has come from harvester, mapped and refined
                        and about to be sent to metax
    :return: data_dict that conforms with metax json format
    '''

    catalog_id = data_dict.pop('data_catalog')
    return {'research_dataset': data_dict, 'data_catalog': catalog_id}