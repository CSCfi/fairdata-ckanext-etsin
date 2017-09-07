import ckanext.etsin.refiners.kielipankki as kielipankki
import ckanext.etsin.refiners.syke as syke


def refine(context, data_dict):
    '''
    Chooses refiner function based on harvest source name.
    '''

    harvest_source_name = context.pop('harvest_source_name', '')

    if harvest_source_name == "kielipankki":
        data_dict = kielipankki.kielipankki_refiner(context, data_dict)
    elif harvest_source_name == "syke":
        data_dict = syke.syke_refiner(context, data_dict)

    return data_dict
