import ckanext.etsin.refiners.kielipankki as kielipankki
import ckanext.etsin.refiners.syke as syke
import ckanext.etsin.refiners.fsd as fsd
from ckanext.etsin.exceptions import DatasetFieldsMissingError


def refine(context, package_dict):
    '''
    Chooses refiner function based on harvest source name.
    '''

    harvest_source_name = context.get('harvest_source_name', '')

    if harvest_source_name == "kielipankki":
        package_dict = kielipankki.kielipankki_refiner(context, package_dict)
    elif harvest_source_name == "syke":
        package_dict = syke.syke_refiner(context, package_dict)
    elif harvest_source_name == "fsd":
        package_dict = fsd.fsd_refiner(context, package_dict)
    else:
        raise DatasetFieldsMissingError(package_dict, "Unable to identify harvest source in refiner: %s", package_dict)

    return package_dict
