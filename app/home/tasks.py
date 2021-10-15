import datetime
import logging
import requests
from celery.decorators import task
from django.conf import settings
from django.utils.timezone import now
# from .models import ServerProfile

logger = logging.getLogger('celery')


# @task(name='notify_guild_app')
# def notify_guild_app(app_id):
#     logger.info('notify_guild_app: executed')
#     app = GuildApplicants.objects.get(id=app_id)
#     message = ('New Guild Application: **{char_name} - {char_role}**\n'
#                'Warcraft Logs: {warcraft_logs}\n'
#                'Raid Experience:```\n{raid_exp}\n```').format(**app.__dict__)
#     send_discord_message(settings.BLUE_DISCORD_APP_CHANNEL, message)
#     return 'Finished'


def send_discord_message(channel_id, message):
    url = '{}/channels/{}/messages'.format(
        settings.DISCORD_API_ENDPOINT,
        channel_id,
    )
    headers = {
        'Authorization': 'Bot {}'.format(settings.ISCORD_BOT_TOKEN),
    }
    data = {'content': message}
    r = requests.post(url, headers=headers, data=data, timeout=10)
    if not r.ok:
        r.raise_for_status()
    return r
