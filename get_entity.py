import json
import os
import re

from tqdm import tqdm


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


def getEntities(json_path, all_entities):
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

    if entity_name:
        if 'Type' not in data:
            tmp = getEntityType(data['Title'])
            if tmp == 'ioctl':
                return
            if entity_name_syntax:
                all_entities[entity_name_syntax] = [
                    entity_type[tmp], data['Url']]
            all_entities[entity_name] = [entity_type[tmp], data['Url']]
        elif data['Type'] == 'method':
            all_entities[getClassName(entity_name)] = [
                entity_type['class'], ""]
            all_entities[getMethodName(entity_name)] = [
                entity_type['method'], data['Url']]
            if entity_name_syntax:
                all_entities[entity_name_syntax] = [
                    entity_type['method'], data['Url']]
        else:
            if entity_name_syntax:
                all_entities[entity_name_syntax] = [
                    entity_type[data['Type']], data['Url']]
            all_entities[entity_name] = [
                entity_type[data['Type']], data['Url']]

    if 'Args' in data:
        for arg in data['Args']:
            if str.lower(arg) in all_entities:
                continue
            all_entities[str.lower(arg)] = [entity_type['param'], ""]

    if 'Requirements' in data:
        if 'Header' in data['Requirements']:
            all_entities[str.lower(data['Requirements']['Header'])] = [
                entity_type['header'], ""]
        if 'Library' in data['Requirements']:
            all_entities[str.lower(data['Requirements']['Library'])] = [
                entity_type['library'], ""]
        if 'DLL' in data['Requirements']:
            all_entities[str.lower(data['Requirements']['DLL'])] = [
                entity_type['dll'], ""]


def printEntitiesInfo(all_entites):
    count_entities = {}
    for t, v in entity_type.items():
        count_entities[v] = 0
    for entity in all_entites:
        count_entities[all_entites[entity][0]] += 1
    print('=========== entities =============')
    for t, v in entity_type.items():
        print('%s: %d' % (t, count_entities[v]))


def getAllEntities():
    global entity_type
    entity_type = {
        'param': 0,
        'class': 1,
        'structure': 2,
        'interface': 3,
        'enumeration': 4,
        'union': 5,
        'method': 6,
        'function': 7,
        'callback function': 8,
        'macro': 9,
        'header': 10,
        'library': 11,
        'dll': 12
    }
    all_entities = {}
    api_dir = './APIs'

    json_files = os.listdir(api_dir)
    for json_file in tqdm(json_files):
        json_file_path = os.path.join(api_dir, json_file)
        getEntities(json_file_path, all_entities)

    with open('entities.json', 'w') as f:
        json.dump(all_entities, f)

    printEntitiesInfo(all_entities)


if __name__ == "__main__":
    getAllEntities()
