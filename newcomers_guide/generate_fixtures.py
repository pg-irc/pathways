import json
from newcomers_guide.system_data import get_system_taxonomies


def generate_task_fixture(tasks):
    header = ('// intended to be located at pathways-frontend/src/fixtures/newcomers_guide/tasks.ts\n'
              '// tslint:disable:quotemark trailing-comma max-line-length\n'
              '\n'
              'import { ValidTaskStore } from \'../types/tasks\';\n'
              '\n'
              'export const buildTasksFixture = (): ValidTaskStore => {\n'
              '    return new ValidTaskStore({\n'
              '        savedTasksList: [],\n')

    footer = ('    });\n'
              '};')

    task_map_as_json = 'taskMap: ' + json.dumps(tasks['taskMap'],
                                                ensure_ascii=False,
                                                sort_keys=True,
                                                indent=4)

    return (header +
            add_leading_spaces(8, task_map_as_json) + '\n' +
            footer)


def generate_taxonomy_fixture(taxonomies):
    header = ('// intended to be located at pathways-frontend/src/fixtures/newcomers_guide/taxonomies.ts\n'
              '// tslint:disable:quotemark trailing-comma max-line-length\n'
              'import { TaxonomyStore } from \'../types/taxonomies\';\n'
              '\n'
              'export const buildTaxonomyFixture = (): TaxonomyStore => ({\n'
              '    taxonomyMap:     ')

    footer = ('\n});')

    taxonomies_as_dictionary = make_dict_from_taxonomies(taxonomies)
    taxonomies_as_json = json.dumps(taxonomies_as_dictionary,
                                    ensure_ascii=False,
                                    sort_keys=True,
                                    indent=4)

    return header + add_leading_spaces(4, taxonomies_as_json) + footer


def make_dict_from_taxonomies(taxonomies):
    result = get_system_taxonomies()

    for term in taxonomies:
        taxonomy_id = term.taxonomy_id
        ensure_map_has_key(result, taxonomy_id, {})

        term_id = term.taxonomy_term_id
        ensure_map_has_key(result[taxonomy_id], term_id, {})

    return result


def ensure_map_has_key(the_map, the_key, the_value):
    if the_key not in the_map:
        the_map[the_key] = the_value


def add_leading_spaces(count, tasks_as_json):
    json_lines = tasks_as_json.split('\n')
    json_lines_with_spaces = map(lambda line: count*' ' + line, json_lines)
    return '\n'.join(json_lines_with_spaces)


def set_taxonomy_term_references_on_content(taxonomy_references, content_fixtures):
    for reference in taxonomy_references:
        if reference.content_id in content_fixtures:
            content = content_fixtures[reference.content_id]
            if 'taxonomyTerms' not in content:
                content['taxonomyTerms'] = []
            content['taxonomyTerms'].append({'taxonomyId': reference.taxonomy_id,
                                             'taxonomyTermId': reference.taxonomy_term_id})
