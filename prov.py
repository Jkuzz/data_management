import time
import re


def update_gen_time(prov_filename, entity_name):
    with open(prov_filename, 'r', encoding='utf-8') as prov_file:
        prov_lines = prov_file.readlines()
    with open(prov_filename, 'w', encoding='utf-8') as prov_file:
        regex = re.compile("ex:loadedData prov:generatedAtTime \".+\"\^\^xsd:dateTime .")
        current_time = time.strftime("%Y-%m-%dT%H:%M:%S")
        for line in prov_lines:
            line = re.sub(
                f"{entity_name} prov:generatedAtTime \".+\"\^\^xsd:dateTime .",
                f"ex:loadedData prov:generatedAtTime \"{current_time}\"^^xsd:dateTime .",
                line
            )
            prov_file.write(line)