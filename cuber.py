import loader
import json
from shutil import copyfile
import prov

INPUT_FILE = 'loaded_data.json'  # This name is given to the loader module
TEMPLATE_FILE = 'template.ttl'
OUTPUT_FILE = 'out.ttl'
PROV_FILE = 'prov.ttl'


def prepare_cubes(input_dict):
    copyfile(TEMPLATE_FILE, OUTPUT_FILE)
    return make_form_concepts(input_dict)


def make_form_concepts(input_dict):
    """Discovers all forms of healthcare and creates their concepts"""
    known_forms = []  # First discover all healthcare forms
    for item in input_dict:
        for form in item['pocty_dle_formy_pece']:
            if form in known_forms:
                continue
            known_forms.append(form)

    with open(OUTPUT_FILE, 'a+', encoding='utf-8') as out_file:
        for i, form in enumerate(known_forms):  # Write each form as concept
            form_string = f'ex:formConcept{i} a skos:Concept ;\n'\
                        f'\trdfs:label "{form}" ;\n'\
                        f'\tskos:inScheme ex:FormConceptScheme .\n\n'
            out_file.write(form_string)

    return known_forms


def make_pop_cube(input_dict):
    """Creates the first data cube from the input dictionary"""
    with open(OUTPUT_FILE, 'a+', encoding='utf-8') as out_file:
        for obs_it, pop_observation in enumerate(input_dict):
            okres = pop_observation['okres']
            year = pop_observation['rok']
            inhabitants = pop_observation['stredni_stav_obyvatel']
            obs_string = f'ex:observation{obs_it} a qb:Observation ;\n' \
                         '\tqb:dataSet ex:dataCubeInhabitants ;\n' \
                         f'\tex:refPeriodDim "{year}"^^xsd:date ;\n' \
                         f'\tex:refAreaDim "{okres}" ;\n' \
                         f'\tex:inhabitantsMsr "{inhabitants}"^^xsd:integer .\n\n'
            out_file.write(obs_string)


def get_inhabitants_concept(inhabitants):
    """This shouldn't be hardcoded but it is :)"""
    if inhabitants < 50000:
        level = 0
    elif inhabitants < 100000:
        level = 1
    elif inhabitants < 150000:
        level = 2
    else:
        level = 3
    return f'ex:inhabitantsConcept{level}'


def make_hc_cube(input_dict, known_forms):
    """Creates the second data cube from the input dictionary"""
    with open(OUTPUT_FILE, 'a+', encoding='utf-8') as out_file:
        for obs_it, observation in enumerate(input_dict):
            if observation['pocty_dle_formy_pece'] == {}:
                continue
            okres = observation['okres']
            year = observation['rok']
            inhabitants = observation['stredni_stav_obyvatel']
            for form_it, hc_form in enumerate(observation['pocty_dle_formy_pece']):
                form = f'ex:formConcept{known_forms.index(hc_form)}'
                form_providers = observation['pocty_dle_formy_pece'][hc_form]
                obs_string = f'ex:observation{obs_it}_{form_it} a qb:Observation ;\n' \
                             '\tqb:dataSet ex:dataCubeHealthcare ;\n' \
                             f'\tex:refPeriodDim "{year}"^^xsd:date ;\n' \
                             f'\tex:refAreaDim "{okres}" ;\n' \
                             f'\tex:inhabitantsDim "{get_inhabitants_concept(inhabitants)}" ;\n' \
                             f'\tex:healthcareFormDim {form} ;\n' \
                             f'\tex:providersMsr "{form_providers}"^^xsd:integer .\n\n'
                out_file.write(obs_string)


def make_cubes(prov_filename):
    """Creates data cubes as per HW2 from data loaded by HW1"""
    with open(INPUT_FILE, 'r', encoding='utf-8') as in_file:
        input_dict = json.load(in_file)['data']

    known_forms = prepare_cubes(input_dict)
    make_pop_cube(input_dict)
    print('Population data cube created.')
    make_hc_cube(input_dict, known_forms)
    print('Healthcare providers data cube created.')
    prov.update_gen_time(prov_filename, "ex:dataCube")


if __name__ == '__main__':
    print('Running cuber pipeline...')
    loader.load(INPUT_FILE, PROV_FILE)
    print('Loading finished.\nCreating data cube...')
    make_cubes(PROV_FILE)
    print('Creation of data cubes finished.')
