import csv
import json
import glob
import prov

# https://data.gov.cz/datov%C3%A1-sada?iri=https%3A%2F%2Fdata.gov.cz%2Fzdroj%2Fdatov%C3%A9-sady%2Fhttps---opendata.mzcr.cz-api-3-action-package_show-id-nrpzs
HEALTHCARE_FILE = 'data/narodni-registr-poskytovatelu-zdravotnich-sluzeb.csv'

# https://data.gov.cz/datov%C3%A1-sada?iri=https%3A%2F%2Fdata.gov.cz%2Fzdroj%2Fdatov%C3%A9-sady%2Fhttp---vdb.czso.cz-pll-eweb-package_show-id-130141r20
# https://data.gov.cz/datov%C3%A1-sada?iri=https%3A%2F%2Fdata.gov.cz%2Fzdroj%2Fdatov%C3%A9-sady%2Fhttp---vdb.czso.cz-pll-eweb-package_show-id-130141r19
population_files = glob.glob('./data/130141-??data20??.csv')

# https://data.gov.cz/datov%C3%A1-sada?iri=https%3A%2F%2Fdata.gov.cz%2Fzdroj%2Fdatov%C3%A9-sady%2Fhttp---vdb.czso.cz-pll-eweb-package_show-id-cis101
OKRES_FILE = 'data/CIS0101_CS.csv'

OUTPUT_FILE = 'out.json'
PROV_FILE = 'prov.ttl'


def load(output_filename, prov_filename):
    """Reads input data files and creates a single data file."""
    out_dict = {}
    okres_dict = {}

    with open(OKRES_FILE, 'r', encoding='cp1250') as okres_file:
        reader_okres = csv.reader(okres_file)
        next(reader_okres)  # skip header
        next(reader_okres)  # skip blank okres
        for row_okres in reader_okres:
            if not row_okres:
                continue
            okres_nuts = row_okres[8]
            okres_dict[row_okres[3]] = okres_nuts

    for p_file_name in population_files:
        year = p_file_name[-8:-4]
        with open(p_file_name, 'r', encoding='utf-8') as csv_file_pop:
            reader_pop = csv.reader(csv_file_pop)
            next(reader_pop)  # skip header
            for row_pop in reader_pop:
                if row_pop and row_pop[2] == 'DEM0004':
                    if row_pop[5] == '101' or row_pop[6] == '554782':
                        if row_pop[5] == '101':  # kod ciselniku hodnoty
                            okres_nuts = okres_dict[row_pop[6]]  # find the okres code using CIS0101
                        elif row_pop[6] == '554782':  # Special case for Praha
                            okres_nuts = 'CZ0100'
                        out_dict[(okres_nuts, year)] = {
                            'okres': okres_nuts,
                            'rok': year,
                            'stredni_stav_obyvatel': 0,
                            'pocty_dle_formy_pece': {}
                        }
                        out_dict[(okres_nuts, year)]['stredni_stav_obyvatel'] += int(row_pop[1])

    with open(HEALTHCARE_FILE, 'r', encoding='utf-8') as csv_file_hc:
        reader_hc = csv.reader(csv_file_hc)
        next(reader_hc)  # skip header
        for row_hc in reader_hc:
            nuts = row_hc[12]
            if not nuts:  # nejaka pani doktorka Ivanka si neumi vyplnit okres Praha, jen Kraj Praha a pak to pada
                nuts = row_hc[10] + '0'  # happens once, kraj Praha => okres Praha
                if nuts not in okres_dict.values():
                    print('Missing okres NUTS in healthcare provider, skipping.')
                    print(row_hc)
                    continue
            all_forms = row_hc[28].split(', ')
            for form in all_forms:
                if not form:
                    continue
                all_forms = out_dict[(nuts, '2019')]['pocty_dle_formy_pece']  # 2019 year hardwired!!
                all_forms[form] = all_forms.get(form, 0) + 1

    with open(output_filename, 'w', encoding='utf-8') as out_file:
        root_dict = {'data': list(out_dict.values())}
        json.dump(root_dict, out_file, indent=4, ensure_ascii=False)

    prov.update_gen_time(prov_filename, "ex:loadedData")


if __name__ == '__main__':
    print('Running standalone loader')
    load(OUTPUT_FILE, PROV_FILE)
