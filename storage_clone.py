import os

from appwrite.client import Client
from appwrite.services.storage import Storage
from appwrite.input_file import InputFile

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


src_storage = Storage(src_client)
dst_storage = Storage(dst_client)


for dst_bucket in tqdm(dst_storage.list_buckets()['buckets'], desc='Deleting buckets from destination project'):
    dst_storage.delete_bucket(dst_bucket['$id'])

for src_bucket in tqdm(src_storage.list_buckets()['buckets'], desc='Creating buckets'):
    dst_storage.create_bucket(src_bucket['$id'], src_bucket['name'], src_bucket['$permissions'], src_bucket['fileSecurity'], src_bucket['enabled'], src_bucket['maximumFileSize'], src_bucket.get('allowedFileExtensions'), src_bucket['compression'], src_bucket['encryption'], src_bucket['antivirus'])

for src_bucket in src_storage.list_buckets()['buckets']:
    bucket_id = src_bucket['$id']

    for src_file in tqdm(src_storage.list_files(bucket_id)['files'], desc=f'Copying files to bucket {src_bucket["name"]}'):
        file_id = src_file['$id']
        file_name = src_file['name']
        file_mime = src_file['mimeType']
        file_perms = src_file['$permissions']
        file_bytes = src_storage.get_file_download(bucket_id, file_id)
        dst_storage.create_file(bucket_id, file_id, InputFile.from_bytes(file_bytes, file_name, file_mime), file_perms)