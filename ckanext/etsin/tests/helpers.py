import os
import json
import time
from lxml import etree


def _get_fixture(filename):
    return os.path.join(os.path.dirname(__file__), "..", "test_fixtures", filename)


def _get_file_as_string(filename):
    with open(_get_fixture(filename)) as file:
        return ''.join(file.readlines())


def _get_file_as_lxml(filename):
    return etree.fromstring(_get_file_as_string(filename))


def _get_json_as_dict(filename):
    with open(_get_fixture(filename)) as file:
        dict = json.loads(''.join(file.readlines()))
    return dict


def _create_identifier_ending():
    ''' Helper for making unique identifiers '''
    return str(int(time.time()))
