import os
import csv
import json
import re
from tqdm import tqdm
from collections import Counter


def loadEntitiesFromFile(path):
    i = 0
    with open(path) as f:
        all_entites = json.load(f)
        for entity in all_entites:
            entity_type = all_entites[entity][0]
            entities_type_dict[entity_type].add(entity)
            if all_entites[entity][1] != "":
                if all_entites[entity][1] in url_to_entity:
                    url_to_entity[all_entites[entity][1]].append(entity)
                else:
                    url_to_entity[all_entites[entity][1]] = [entity]
            if entity not in entity_id_mapping:
                i += 1
                entity_id_mapping[entity] = i


def getEntityName(s):
    pattern = re.compile(r'(\S+)\s(.+)')
    result = pattern.match(s)
    if result:
        return str.lower(result.group(1))


def getEntityNameSyntax(s):
    pattern = re.compile(r'(\S+\s)+([_A-Za-z0-9]+)\s*(\{|\(|;)\n')
    result = pattern.match(s)
    if result:
        return str.lower(result.group(2))


def getEntityType(s):
    pattern = re.compile(r'(\S+)\s(\S+)\s(.+)')
    result = pattern.match(s)
    if result:
        return str.lower(result.group(2))


def getClassName(s):
    pattern = re.compile(r'(.+)::(.+)')
    result = pattern.match(s)
    if result:
        return str.lower(result.group(1))


def getMethodName(s):
    pattern = re.compile(r'(.+)::(.+)')
    result = pattern.match(s)
    if result:
        return str.lower(result.group(2))


def addEntityRelation(entity_name, entity_name_syntax, r_type, r_to):
    entity_relations.add(
        (entity_id_mapping[entity_name], relation_type[r_type], entity_id_mapping[str.lower(r_to)]))
    if entity_name_syntax:
        entity_relations.add(
            (entity_id_mapping[entity_name_syntax], relation_type[r_type], entity_id_mapping[str.lower(r_to)]))


def getRelations(json_path):
    if not os.path.exists(json_path):
        return

    data = json.load(open(json_path))
    if 'Title' in data:
        entity_name = getEntityName(data['Title'])
    else:
        entity_name = None
    if 'Syntax' in data:
        entity_name_syntax = getEntityNameSyntax(data['Syntax'])
    else:
        entity_name_syntax = None
    if 'Type' in data:
        entity_type = data['Type']
    else:
        entity_type = getEntityType(data['Title'])
    if entity_type == 'ioctl':
        return

    # method_of
    if entity_type == 'method' and entity_name:
        class_name = getClassName(entity_name)
        method_name = getMethodName(entity_name)
        entity_name = method_name
        addEntityRelation(entity_name, entity_name_syntax,
                          'method_of', class_name)

    # return & param
    if 'Arg' in data:
        arg_len = len(data['Arg'])
        if arg_len > 0:
            if entity_type == 'callback function' or entity_type == 'function' or entity_type == 'method':
                addEntityRelation(
                    entity_name, entity_name_syntax, 'return', data['Arg'][0])
            elif entity_type == 'structure' or entity_type == 'union':
                addEntityRelation(
                    entity_name, entity_name_syntax, 'param', data['Arg'][0])

        for i in range(1, arg_len):
            addEntityRelation(entity_name, entity_name_syntax,
                              'param', data['Arg'][i])

    # use_header & use_library & use_dll
    if 'Requirements' in data:
        if 'Header' in data['Requirements']:
            addEntityRelation(entity_name, entity_name_syntax,
                              'use_header', data['Requirements']['Header'])
        if 'Library' in data['Requirements']:
            addEntityRelation(entity_name, entity_name_syntax,
                              'use_library', data['Requirements']['Library'])
        if 'DLL' in data['Requirements']:
            addEntityRelation(entity_name, entity_name_syntax,
                              'use_dll', data['Requirements']['DLL'])

    # releation_normal # releation_conceptual # releation_other_resources # releation_reference
    if 'see-also' in data:
        if 'Normal' in data['see-also']:
            for url in data['see-also']['Normal']:
                if url in url_to_entity:
                    for entity in url_to_entity[url]:
                        addEntityRelation(entity_name, entity_name_syntax,
                                          'releation_normal', entity)
        if 'Conceptual' in data['see-also']:
            for url in data['see-also']['Conceptual']:
                if url in url_to_entity:
                    for entity in url_to_entity[url]:
                        addEntityRelation(entity_name, entity_name_syntax,
                                          'releation_conceptual', entity)
        if 'Other Resources' in data['see-also']:
            for url in data['see-also']['Other Resources']:
                if url in url_to_entity:
                    for entity in url_to_entity[url]:
                        addEntityRelation(entity_name, entity_name_syntax,
                                          'releation_other_resources', entity)
        if 'Reference' in data['see-also']:
            for url in data['see-also']['Reference']:
                if url in url_to_entity:
                    for entity in url_to_entity[url]:
                        addEntityRelation(entity_name, entity_name_syntax,
                                          'releation_reference', entity)


def save_relations():
    id_entity_mapping = {}
    for entity, entity_id in entity_id_mapping.items():
        id_entity_mapping[entity_id] = entity

    id_relation_mapping = {}
    for relation, relation_id in relation_type.items():
        id_relation_mapping[relation_id] = relation

    save_relations = [list(_) for _ in entity_relations]
    save_relations.sort(key=lambda x: x[0])
    save_relations_readable = [[id_entity_mapping[_[0]], id_relation_mapping[_[
        1]], id_entity_mapping[_[2]]] for _ in save_relations]

    with open('relations.txt', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(save_relations)

    with open('relations_readable.txt', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(save_relations_readable)

    c_relation = Counter(_[1] for _ in save_relations_readable)
    print('\n\n=========== relations ==========')
    for r, c in c_relation.items():
        print('%s: %d' % (r, c))


def getAllRelations():
    global relation_type, entities_type_dict, entity_relations, entity_id_mapping, url_to_entity
    relation_type = {
        'method_of': 1,
        'return': 2,
        'param': 3,
        'use_header': 4,
        'use_library': 5,
        'use_dll': 6,
        'releation_normal': 7,
        'releation_conceptual': 8,
        'releation_other_resources': 9,
        'releation_reference': 10
    }
    entities_type_dict = {
        0: set(),
        1: set(),
        2: set(),
        3: set(),
        4: set(),
        5: set(),
        6: set(),
        7: set(),
        8: set(),
        9: set(),
        10: set(),
        11: set(),
        12: set()
    }
    entity_relations = set()
    entity_id_mapping = {}
    url_to_entity = {}

    loadEntitiesFromFile('entities.json')

    api_dir = './APIs'
    json_files = os.listdir(api_dir)
    print('All json files: %d' % len(json_files))

    for json_file in tqdm(json_files):
        json_file_path = os.path.join(api_dir, json_file)
        getRelations(json_file_path)

    save_relations()


if __name__ == "__main__":
    getAllRelations()
