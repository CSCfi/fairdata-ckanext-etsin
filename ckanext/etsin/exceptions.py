# This file is part of the Etsin harvester service
#
# Copyright 2017-2018 Ministry of Education and Culture, Finland
#
# :author: CSC - IT Center for Science Ltd., Espoo Finland <servicedesk@csc.fi>
# :license: GNU Affero General Public License version 3

class DatasetFieldsMissingError(Exception):
    """Basic exception for situation when a dataset can't be
      sent to Metax due to missing relevant fields"""

    def __init__(self, package_dict, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = "Package missing relevant fields: %s" % package_dict
        super(DatasetFieldsMissingError, self).__init__(msg)