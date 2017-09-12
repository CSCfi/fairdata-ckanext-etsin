from ckanext.harvest.model import HarvestObject


def get_iso_values_dict_1():
    ho = HarvestObject()
    ho.guid = 'M28mitl:'
    return {
        'iso_values': _get_valid_iso_values_dict_1(),
        'harvest_object': ho
    }


def _get_valid_iso_values_dict_1():
    return {
        'title': 'Testiaineisto',
        'responsible-organisation': [
            {
                'organisation-name': 'omistaja',
                'contact-info': {'email': 'omistaja@testi.fi'},
                'role': ['owner']
            },
            {
                'organisation-name': 'tekija1',
                'contact-info': {'email': 'tekija1@testi.fi'
                                 },
                'role': ['originator']
            },
            {
                'organisation-name': 'tekija2',
                'contact-info': {'email': 'tekija2@testi.fi'
                                 },
                'role': ['originator']
            },
            {
                'organisation-name': 'kuratoija',
                'contact-info': {'email': 'kuratoija@testi.fi'
                                 },
                'role': ['pointOfContact']
            },
            {
                'organisation-name': 'jakelija',
                'contact-info': {'email': 'jakelija@testi.fi'
                                 },
                'role': ['distributor']
            },
            {
                'organisation-name': 'julkaisija',
                'contact-info': {'email': 'julkaisija@testi.fi'
                                 },
                'role': ['publisher']
            },
            {
                'organisation-name': 'jotainmuuta',
                'contact-info': {'email': 'jotainmuuta@testi.fi'
                                 },
                'role': ['user']
            },
        ],
        'metadata-language': 'fin',
        'abstract': 'kuvailuteksti',
        'dataset-language': ['fin'],
        'tags': ['testiavainsana'],
        'bbox': [{'west': '21.193932', 'east': '23.154996', 'north': '60.87458', 'south': '59.880178'}],
        'date-released': '2017-01-01',
        'date-updated': '2017-06-06',
        'use-constraints': ['joopajoo'],
        'temporal-extent-begin': ['2000-01-01'],
        'temporal-extent-end': ['2001-01-01'],
        'lineage': 'provenance'
    }


def get_package_dict_1():
    return {'access_rights': {'description': [{'fi': 'joopajoo'}]},
            'creator': [{'email': 'tekija1@testi.fi', 'name': 'tekija1'},
                        {'email': 'tekija2[a]testi.fi', 'name': 'tekija2'}],
            'curator': [{'email': 'kuratoija[at]testi.fi', 'name': 'kuratoija'}],
            'description': [{'fi': 'kuvailuteksti'}],
            'issued': '2017-01-01',
            'keyword': ['testiavainsana'],
            'language': [{'identifier': 'http://lexvo.org/id/iso639-3/fin'}],
            'modified': '2017-06-06',
            'preferred_identifier': 'M28mitl:',
            'provenance': [{'description': 'provenance'}],
            'publisher': {'email': 'jakelija [a] testi.fi', 'name': 'jakelija'},
            'rights_holder': {'email': 'omistaja [at] testi.fi', 'name': 'omistaja'},
            'spatial': [{
                            'polygon': 'POLYGON((59.880178 21.193932,59.880178 23.154996,60.87458 23.154996,60.87458 21.193932,59.880178 21.193932))'}],
            'temporal': [{'end_date': '2001-01-01', 'start_date': '2000-01-01'}],
            'title': [{'fi': 'Testiaineisto'}]}
