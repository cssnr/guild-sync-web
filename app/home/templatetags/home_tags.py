import urllib.parse
from django import template
from django.conf import settings
from django.urls import reverse

# import logging
# logger = logging.getLogger('app')

register = template.Library()


@register.simple_tag(name='get_config')
def get_config(value):
    try:
        return getattr(settings, value)
    except:
        return None


@register.simple_tag(name='get_bot_url')
def get_bot_url(serverid):
    try:
        base_url = 'https://discord.com/api/oauth2/authorize'
        # reverse_url = reverse('home:server', kwargs={'serverid': serverid})
        # redirect_url = '{}{}'.format(settings.DISCORD_BOT_REDIRECT, reverse_url)
        safe_redirect_url = urllib.parse.quote_plus(settings.DISCORD_BOT_REDIRECT)
        url = '{}?permissions=8&scope=bot&client_id={}&guild_id={}&redirect_uri={}&response_type=code'.format(
            base_url, settings.OAUTH_CLIENT_ID, serverid, safe_redirect_url)
        return url
    except:
        return None
