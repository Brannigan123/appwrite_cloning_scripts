import os

from appwrite.client import Client
from appwrite.services.teams import Teams

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


src_teams = Teams(src_client)
dst_teams = Teams(dst_client)


for dst_team in tqdm(dst_teams.list()['teams'], desc='Deleting teams from destination project'):
    dst_teams.delete(dst_team['$id'])

for src_team in tqdm(src_teams.list()['teams'], desc='Creating teams'):
    dst_teams.create(src_team['$id'], src_team['name'], src_team.get('roles'))

for src_team in src_teams.list()['teams']:
    team_id = src_team['$id']

    for src_memb in tqdm(src_teams.list_memberships(team_id)['memberships'], desc=f'Adding members to team {src_team["name"]}'):
        memb_roles = src_memb['roles']
        memb_email = src_memb.get('userEmail')
        memb_user_id = src_memb['userId']
        memb_phone = src_memb.get('userPhone')
        memb_name = src_memb['userName']

        dst_teams.create_membership(team_id, memb_roles, "https://cloud.appwrite.io/v1", memb_email, memb_user_id, memb_phone, memb_name)
       