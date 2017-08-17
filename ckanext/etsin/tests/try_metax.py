"""
This script is a temporary quick helper for manually checking if a given
dataset dictionary object is currently accepted by the MetaX API.
"""
import ckanext.etsin.metax_api as api
import helpers
import os

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    filename = 'minimum_valid_edited.json'
    filepath = os.path.join('metax_json_dicts', filename)
    dataset = helpers._get_json_as_dict(
        'metax_json_dicts/minimum_valid_edited.json')
    dataset['research_dataset']['preferred_identifier'] += helpers._create_identifier_ending()
    dataset['research_dataset']['urn_identifier'] += helpers._create_identifier_ending()
    print "Posting dataset {} with identifier {}".format(filename, dataset['research_dataset']['urn_identifier'])
    id = api.create_dataset(dataset)
    print "Dataset was posted and it was assigned id {}".format(id)
    print "Checking if MetaX knows it exists"
    print api.check_dataset_exists(dataset['research_dataset']['preferred_identifier'])
    print "Replacing dataset (with same dataset)"
    api.replace_dataset(id, dataset)
    print "Deleting the dataset from MetaX"
    api.delete_dataset(id)
    print "Success!"
