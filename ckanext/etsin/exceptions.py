class DatasetFieldsMissingError(Exception):
    """Basic exception for situation when a dataset can't be
      sent to Metax due to missing relevant fields"""

    def __init__(self, package_dict, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = "Package missing relevant fields: %s" % package_dict
        super(DatasetFieldsMissingError, self).__init__(msg)