import urllib.parse
from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag(name='get_config')
def get_config(value):
    try:
        return getattr(settings, value)
    except:
        return None


@register.filter(name='tag_to_class')
def tag_to_class(value):
    return {
        'info': 'primary',
        'success': 'success',
        'warning': 'warning',
        'error': 'danger',
    }[value]


@register.filter(name='theme_css')
def theme_css(value=None):
    if value not in settings.SITE_THEMES:
        value = 'default'
    theme = settings.SITE_THEMES[value]
    return theme['css']


@register.simple_tag(name='get_bot_url')
def get_bot_url(serverid):
    try:
        base_url = 'https://discord.com/api/oauth2/authorize'
        safe_redirect_url = urllib.parse.quote_plus(settings.DISCORD_BOT_REDIRECT)
        url = '{}?permissions=8&scope=bot&client_id={}&guild_id={}&redirect_uri={}&response_type=code'.format(
            base_url, settings.OAUTH_CLIENT_ID, serverid, safe_redirect_url)
        return url
    except:
        return None
