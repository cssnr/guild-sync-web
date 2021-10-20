import logging
import requests
from celery.decorators import task
from django.conf import settings
from django.core import management
from oauth.models import CustomUser
from home.models import ServerProfile

logger = logging.getLogger('celery')


@task(autoretry_for=(Exception,))
def clear_sessions():
    return management.call_command('clearsessions')


@task()
def process_upload(user_pk, data):
    user = CustomUser.objects.get(pk=user_pk)
    logger.info(user.server_list)
    for g in data['guilds']:
        logger.info(data['guilds'][g])
        guild = g.split('-')[0]
        realm = g.split('-')[1]
        logger.info('guild: %s', guild)
        logger.info('realm: %s', realm)
        server = ServerProfile.objects.get_by_guild(guild, realm)
        logger.info(server)
        if server and server.server_id in user.server_list:
            logger.info('Matching Configuration: %s', server.server_id)
            logger.info(server)
            r = get_guild_users(server.server_id)
            if not r.ok:
                r.raise_for_status()
            users = r.json()
            for user in users:
                if server.sync_method == 'note':
                    # note sync
                    logger.info('Note Sync.')
                    discord_user = '{}#{}'.format(
                        user['user']['username'],
                        user['user']['discriminator'],
                    )
                    match = match_note(data['guilds'][g], discord_user)
                elif server.sync_method == 'name':
                    # name sync
                    logger.info('Name Sync.')
                    discord_user = user['nick'] if user['nick'] else user['user']['username']
                    match = match_name(data['guilds'][g], discord_user)
                    pass
                else:
                    logger.warning('Unknown sync_method: %s', server.sync_method)
                    continue

                if match:
                    logger.info('Will Process Match Here!')
                    logger.info(match)
                    if server.guild_role and \
                            server.guild_role not in user['roles']:
                        logger.info('Adding %s to role %s',
                                     user['user']['username'],
                                     server.guild_role)
                        r = add_guild_role(server.server_id,
                                           user['user']['id'],
                                           server.guild_role)
                        logger.info(r.status_code)
                        logger.info(r.content.decode('utf-8'))
                        if not r.ok:
                            logger.error('Error adding role to user.')
                        else:
                            logger.info('Updated user successfully.')


def match_note(guild_data, discord_user):
    logger.info('discord_user: %s', discord_user)
    for user, data in guild_data.items():
        if data[2] == discord_user:
            logger.info('Matched User: %s', discord_user)
            return user
    return None


def match_name(guild_data, username):
    logger.info('username: %s', username)
    for user, data in guild_data.items():
        if user and username:
            user_only = user.split('-')[0]
            if user_only.lower() == username.lower():
                logger.info('Matched User: %s', username)
                return user
    return None


def get_guild_users(serverid):
    params = {'limit': 1000}
    url = f'{settings.DISCORD_API_URL}/guilds/{serverid}/members'
    return discord_api_call(url, settings.DISCORD_BOT_TOKEN, params=params)


def add_guild_role(guildid, userid, roleid):
    api_base = settings.DISCORD_API_URL
    url = f'{api_base}/guilds/{guildid}/members/{userid}/roles/{roleid}'
    logger.info('discord_api_call')
    headers = {'Authorization': f'Bot {settings.DISCORD_BOT_TOKEN}'}
    return requests.put(url, headers=headers, timeout=6)


def discord_api_call(url, token, tt='Bot', params=None):
    logger.info('discord_api_call')
    headers = {'Authorization': f'{tt} {token}'}
    return requests.get(url, params=params, headers=headers, timeout=6)


def send_discord_message(channel_id, message):
    url = f'{settings.DISCORD_API_URL}/channels/{channel_id}/messages'
    headers = {
        'Authorization': f'Bot {settings.DISCORD_BOT_TOKEN}',
    }
    data = {'content': message}
    r = requests.post(url, headers=headers, data=data, timeout=10)
    if not r.ok:
        r.raise_for_status()
    return r
