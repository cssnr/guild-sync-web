import logging
import requests
import time
from celery import shared_task
from django.conf import settings
from django.core import management
from oauth.models import CustomUser
from home.models import ServerProfile

logger = logging.getLogger('celery')


@shared_task()
def clear_sessions():
    return management.call_command('clearsessions')


@shared_task()
def process_upload(user_pk, data):
    user = CustomUser.objects.get(pk=user_pk)
    logger.info(user.server_list)
    for g in data['guilds']:
        # logger.info(data['guilds'][g])
        guild = g.split('-')[0]
        realm = g.split('-')[1]
        logger.info('guild: %s', guild)
        logger.info('realm: %s', realm)
        server = ServerProfile.objects.get_by_guild(guild, realm)
        logger.info(server)
        if server and server.server_id in user.server_list:
            logger.info('Matching Configuration: %s', server.server_id)
            r = get_guild_users(server.server_id)
            logger.info('time.sleep.3')
            time.sleep(3)
            if not r.ok:
                r.raise_for_status()
            users = r.json()
            logger.info('server.sync_method: %s', server.sync_method)
            if server.sync_classes or server.create_roles:
                logger.info('Sync classes or create roles enabled, fetching roles for later.')
                roles = get_guild_roles(server.server_id)
                logger.info(roles)
                logger.info('time.sleep.3')
                time.sleep(3)
            if server.create_roles:
                logger.info('Create Roles enabled, creating roles now...')
                create_roles(server, roles)
            for user in users:
                if server.sync_method == 'note':
                    # note sync
                    discord_user = f"{user['user']['username']}#{user['user']['discriminator']}"
                    user_match = match_note(data['guilds'][g], discord_user)
                elif server.sync_method == 'name':
                    # name sync
                    discord_user = user['nick'] if user['nick'] else user['user']['username']
                    user_match = match_name(data['guilds'][g], discord_user)
                    pass
                else:
                    logger.warning('UNKNOWN server.sync_method: %s', server.sync_method)
                    user_match = None
                    continue

                if user_match:
                    logger.info('Will Process Match Here!')
                    logger.info(type(user_match))
                    logger.info(user_match)
                    if server.guild_role and \
                            server.guild_role not in user['roles']:
                        logger.info('Adding %s to role %s',
                                    user['user']['username'],
                                    server.guild_role)
                        r = add_role_to_user(server.server_id,
                                           user['user']['id'],
                                           server.guild_role)
                        logger.info(r.status_code)
                        logger.info(r.content.decode('utf-8'))
                        if not r.ok:
                            logger.error('Error adding role to user.')
                        else:
                            logger.info('Updated user successfully.')
                        logger.info('time.sleep.3')
                        time.sleep(3)
                    if server.sync_classes:
                        logger.info('Sync classes enabled, checking for role match.')
                        role_match = match_class_role(roles, user_match)
                        if role_match and role_match['id'] not in user['roles']:
                            logger.info('Matching Class Role: %s', role_match['id'])
                            r = add_role_to_user(server.server_id,
                                                 user['user']['id'],
                                                 role_match['id'])
                            logger.info(r.status_code)
                            logger.info(r.content.decode('utf-8'))
                            if not r.ok:
                                logger.error('Error adding role to user.')
                            else:
                                logger.info('Updated user successfully.')
                            logger.info('time.sleep.3')
                            time.sleep(3)
                        pass


def match_class_role(roles, user):
    for role in roles:
        # logger.info('%s <-> %s', role['name'].lower(), user[1].lower())
        if role['name'].lower() == user[1].lower():
            logger.info('MATCH Role: %s', role['id'])
            return role
    return None


def match_note(guild_data, discord_user):
    for user, data in guild_data.items():
        # logger.info('%s <-> %s', data[2], discord_user)
        if data[2] == discord_user:
            logger.info('MATCH User: %s', discord_user)
            return [user] + list(data)
    return None


def match_name(guild_data, username):
    for user, data in guild_data.items():
        if user and username:
            user_only = user.split('-')[0]
            # logger.info('%s <-> %s', user_only, username)
            if user_only.lower() == username.lower():
                logger.info('MATCH Name: %s', username)
                return [user] + list(data)
    return None


def match_role(role_name, roles):
    for role in roles:
        if role_name == role['name'].lower():
            return True
    return False


def create_roles(server, roles):
    role_colors = {
        'druid': '16743434',
        'hunter': '11195250',
        'mage': '4179947',
        'paladin': '16026810',
        'priest': '16777215',
        'rogue': '16774248',
        'shaman': '28893',
        'warlock': '8882414',
        'warrior': '13015917',
    }
    for role_name, color in role_colors.items():
        logger.info('Checking Role: %s', role_name)
        exists = match_role(role_name, roles)
        if not exists:
            logger.info('Creating Role: %s', role_name)
            r = create_role(server.server_id,
                            role_name.title(),
                            color=color,
                            mentionable=True)
            if not r.ok:
                logger.error('Error Crating Role: %s', role_name)
                logger.error(r.status_code)
                logger.error(r.content.decode('utf-8'))
            else:
                logger.info('Role Created Successfully: %s', role_name)
            logger.info('time.sleep.5')
            time.sleep(5)


def get_guild_users(serverid):
    params = {'limit': 1000}
    url = f'{settings.DISCORD_API_URL}/guilds/{serverid}/members'
    return discord_api_call(url, settings.DISCORD_BOT_TOKEN, params=params)


def add_role_to_user(guildid, userid, roleid):
    api_base = settings.DISCORD_API_URL
    url = f'{api_base}/guilds/{guildid}/members/{userid}/roles/{roleid}'
    headers = {'Authorization': f'Bot {settings.DISCORD_BOT_TOKEN}'}
    logger.info('discord_api_call')
    return requests.put(url, headers=headers, timeout=6)


def create_role(guildid, name, color=None, mentionable=False):
    logger.info('guildid: %s', guildid)
    url = f'{settings.DISCORD_API_URL}/guilds/{guildid}/roles'
    logger.info('url: %s', url)
    headers = {'Authorization': f'Bot {settings.DISCORD_BOT_TOKEN}'}
    data = {'name': name, 'color': color, 'mentionable': mentionable}
    logger.info(data)
    logger.info('discord_api_call')
    return requests.post(url, headers=headers, json=data, timeout=6)


def get_guild_roles(serverid):
    url = f'{settings.DISCORD_API_URL}/guilds/{serverid}/roles'
    r = discord_api_call(url, settings.DISCORD_BOT_TOKEN)
    if not r.ok:
        return r
    role_list = []
    for role in r.json():
        if not role['managed'] and not role['position'] == 0:
            role_list.append(role)
    logger.info(role_list)
    return role_list


def send_discord_message(channel_id, message):
    url = f'{settings.DISCORD_API_URL}/channels/{channel_id}/messages'
    headers = {'Authorization': f'Bot {settings.DISCORD_BOT_TOKEN}'}
    data = {'content': message}
    r = requests.post(url, headers=headers, data=data, timeout=10)
    if not r.ok:
        r.raise_for_status()
    return r


def discord_api_call(url, token, tt='Bot', params=None):
    logger.info('discord_api_call')
    headers = {'Authorization': f'{tt} {token}'}
    return requests.get(url, params=params, headers=headers, timeout=6)
