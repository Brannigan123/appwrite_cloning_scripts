import os

from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.exception import AppwriteException

from tqdm import tqdm

from dotenv import load_dotenv
load_dotenv()

src_client = Client()
src_client.set_endpoint(os.getenv('SRC_ENDPOINT'))
src_client.set_project(os.getenv('SRC_PROJECT'))
src_client.set_key(os.getenv('SRC_KEY'))

dst_client = Client()
dst_client.set_endpoint(os.getenv('DST_ENDPOINT'))
dst_client.set_project(os.getenv('DST_PROJECT'))
dst_client.set_key(os.getenv('DST_KEY'))


src_dbs = Databases(src_client)
dst_dbs = Databases(dst_client)

for dst_db in tqdm(dst_dbs.list()['databases'], desc='Deleting databases from destination project'):
    dst_dbs.delete(dst_db['$id'])

for src_db in tqdm(src_dbs.list()['databases'], desc='Creating databases'):
    dst_dbs.create(src_db['$id'], src_db['name'])

for src_db in src_dbs.list()['databases']:
    db_id = src_db['$id']

    for src_col in src_dbs.list_collections(db_id)['collections']:
        col_id = src_col['$id']
        col_name = src_col['name']
        col_perms = src_col['$permissions']
        col_doc_sec = src_col['documentSecurity']

        dst_dbs.create_collection(db_id, col_id, col_name, col_perms, col_doc_sec)
        for attr in tqdm(src_col['attributes'], desc=f'Creating attributes for collection {col_name} in {src_db["name"]} DB'):
            try:
                attr_key = attr['key']
                attr_req = attr['required']
                attr_array = attr['array']

                match attr.get('format'):
                    case 'email':
                        dst_dbs.create_email_attribute(db_id, col_id, attr_key, attr_req, attr['default'])
                    case 'enum':
                        dst_dbs.create_enum_attribute(db_id, col_id, attr_key, attr['elements'], attr_req, attr['default'], attr_array)
                    case 'url':
                        dst_dbs.create_url_attribute(db_id, col_id, attr_key, attr_req, attr['default'], attr_array)
                    case 'ip':
                        dst_dbs.create_ip_attribute(db_id, col_id, attr_key, attr_req, attr['default'], attr_array)
                    case 'datetime':
                        dst_dbs.create_datetime_attribute(db_id, col_id, attr_key, attr_req, attr['default'], attr_array)
                    case _:
                        match attr.get('type'):
                            case 'string':
                                dst_dbs.create_string_attribute(db_id, col_id, attr_key, attr['size'], attr_req, attr['default'], attr_array)
                            case 'integer':
                                dst_dbs.create_integer_attribute(db_id, col_id, attr_key, attr_req, attr['min'], attr['max'], attr['default'], attr_array)
                            case 'double':
                                dst_dbs.create_float_attribute(db_id, col_id, attr_key, attr_req, attr['min'], attr['max'], attr['default'], attr_array)
                            case 'boolean':
                                dst_dbs.create_boolean_attribute(db_id, col_id, attr_key, attr_req, attr['default'], attr_array)
                            case 'relationship':
                                dst_dbs.create_relationship_attribute(db_id, col_id, attr['relatedCollection'], attr['relationType'], attr['twoWay'], attr_key, attr['twoWayKey'], attr['onDelete'] )
            except AppwriteException:
                print(f'Failed to create attribute ${attr}')

        for index in tqdm(src_dbs.list_indexes(db_id, col_id)['indexes'], desc=f'Creating indixes for collection {col_name} in {src_db["name"]} DB'):
            dst_dbs.create_index(db_id, col_id, index['key'], index['type'], index['attributes'], index['orders'])


    for src_col in src_dbs.list_collections(db_id)['collections']:
        col_id = src_col['$id']
        col_name = src_col['name']

        for doc in tqdm(src_dbs.list_documents(db_id, col_id)['documents'], desc=f'Copying data to collection {col_name}'):
            data =  {k: v for k, v in doc.items() if not k.startswith('$')}
            dst_dbs.create_document(db_id, col_id, doc['$id'], data, doc['$permissions'] )
