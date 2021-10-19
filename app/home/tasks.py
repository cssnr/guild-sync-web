import logging
import requests
from celery.decorators import task
from django.conf import settings
from django.core import management
from oauth.models import CustomUser
from home.models import ServerProfile

logger = logging.getLogger('app')


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
        query = ServerProfile.objects.get_by_guild(guild, realm)
        logger.debug(query)
        if query and query.server_id in user.server_list:
            logger.info('Matching Configuration - Processing...')
            logger.debug(query)
        pass
    pass


def send_discord_message(channel_id, message):
    url = '{}/channels/{}/messages'.format(
        settings.DISCORD_API_URL,
        channel_id,
    )
    headers = {
        'Authorization': 'Bot {}'.format(settings.DISCORD_BOT_TOKEN),
    }
    data = {'content': message}
    r = requests.post(url, headers=headers, data=data, timeout=10)
    if not r.ok:
        r.raise_for_status()
    return r
