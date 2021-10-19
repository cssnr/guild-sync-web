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
    logger.debug(user.server_list)
    for g in data['guilds']:
        guild = g.split('-')[0]
        realm = g.split('-')[1]
        logger.debug('guild: %s', guild)
        logger.debug('realm: %s', realm)
        server = ServerProfile.objects.get_by_guild(guild, realm)
        logger.debug(server)
        if server and server.server_id in user.server_list:
            logger.info('Matching Configuration: %s', server.server_id)
            logger.debug(server)
            r = get_guild_users(server.server_id)
            if not r.ok:
                r.raise_for_status()
            users = r.json()
            # logger.debug(users)
            if server.sync_method == 'note':
                logger.debug('Note Sync.')
                logger.debug(data['guilds'][g])
                for user in users:
                    discord_user = '{}#{}'.format(
                        user['user']['username'],
                        user['user']['discriminator'],
                    )
                    match = match_note(data['guilds'][g], discord_user)
                    if match:
                        logger.debug('Will Process Match Here!')
                        logger.debug(match)
                        if server.guild_role and \
                                server.guild_role not in user['roles']:
                            logger.debug('Adding %s to role %s',
                                         user['user']['username'],
                                         server.guild_role)
                            r = add_guild_role(server.server_id,
                                               user['user']['id'],
                                               server.guild_role)
                            logger.debug(r.status_code)
                            logger.debug(r.content.decode('utf-8'))
                            if not r.ok:
                                logger.error('Error adding role to user.')
                            else:
                                logger.info('Updated user successfully.')
            elif server.sync_method == 'name':
                logger.debug('Name Sync.')
                pass
            else:
                logger.warning('Unknown sync_method: %s', server.sync_method)


def match_note(guild_data, username):
    for user, data in guild_data.items():
        if data[2] == username:
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
