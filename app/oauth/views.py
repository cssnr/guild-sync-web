import logging
import requests
import urllib.parse
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import HttpResponseRedirect, redirect
from django.views.decorators.http import require_http_methods
from .models import CustomUser
from home.views import get_user_servers, get_server_id_list

logger = logging.getLogger('app')


def oauth_start(request):
    """
    # View  /oauth/
    """
    request.session['login_redirect_url'] = get_next_url(request)
    params = {
        'client_id': settings.OAUTH_CLIENT_ID,
        'redirect_uri': settings.OAUTH_REDIRECT_URI,
        'response_type': 'code',
        'scope': settings.OAUTH_SCOPE,
    }
    url_params = urllib.parse.urlencode(params)
    url = f'https://discord.com/api/oauth2/authorize?{url_params}'
    return HttpResponseRedirect(url)


def oauth_callback(request):
    """
    # View  /oauth/callback/
    """
    try:
        auth_data = get_access_token(request.GET['code'])
        profile = get_user_profile(auth_data)
        user = login_user(request, profile)
        post_login_actions(request)
        messages.info(request, f'Successfully logged in as {user.first_name}.')
    except Exception as error:
        logger.exception(error)
        messages.error(request, f'Exception during login: {error}')
    next_url = '/'
    if 'login_redirect_url' in request.session:
        next_url = request.session['login_redirect_url']
    logger.debug('login_redirect_url: %s', next_url)
    return HttpResponseRedirect(next_url)


@require_http_methods(['POST'])
def oauth_logout(request):
    """
    View  /oauth/logout/
    """
    next_url = get_next_url(request)
    # Hack to prevent login loop when logging out on a secure page
    logger.debug('next_url: %s', next_url.split('/')[1])
    if next_url.split('/')[1] in ['profile', 'server']:
        logger.debug('Protected View. Changing: next_url')
        next_url = '/'
    logger.debug('login_next_url: %s', next_url)
    request.session['login_next_url'] = next_url
    logout(request)
    return redirect(next_url)


def login_user(request, profile):
    """
    Login or create user
    """
    user, _ = CustomUser.objects.get_or_create(username=profile['id'])
    update_profile(user, profile)
    login(request, user)
    return user


def get_access_token(code):
    """
    Post OAuth code and Return access_token
    """
    url = f'{settings.DISCORD_API_URL}/oauth2/token'
    data = {
        'client_id': settings.OAUTH_CLIENT_ID,
        'client_secret': settings.OAUTH_CLIENT_SECRET,
        'grant_type': settings.OAUTH_GRANT_TYPE,
        'redirect_uri': settings.OAUTH_REDIRECT_URI,
        'code': code,
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.post(url, data=data, headers=headers, timeout=10)
    if not r.ok:
        logger.warning('status_code: %s', r.status_code)
        logger.warning('content: %s', r.content)
    return r.json()


def get_user_profile(data):
    """
    Get Profile for Authenticated User
    """
    url = f'{settings.DISCORD_API_URL}/users/@me'
    headers = {'Authorization': f"Bearer {data['access_token']}"}
    logger.debug('API CALL')
    r = requests.get(url, headers=headers, timeout=10)
    logger.debug('status_code: %s', r.status_code)
    logger.debug('content: %s', r.content)
    p = r.json()
    return {
        'id': p['id'],
        'username': p['username'],
        'discriminator': p['discriminator'],
        'avatar': p['avatar'],
        'access_token': data['access_token'],
        'refresh_token': data['refresh_token'],
        'expires_in': datetime.now() + timedelta(0, data['expires_in']),
    }


def update_profile(user, profile):
    """
    Update Django user profile with provided data
    """
    user.first_name = profile['username']
    user.last_name = profile['discriminator']
    user.discriminator = profile['discriminator']
    user.avatar_hash = profile['avatar']
    user.access_token = profile['access_token']
    user.save()
    return


def post_login_actions(request):
    server_list = get_user_servers(request.user.access_token)
    if isinstance(server_list, requests.models.Response):
        logger.error(server_list.content)
        messages.warning(request, 'Error getting server list from Discord API.')
        return
    logger.debug('server_list: %s', server_list)
    request.user.server_list = get_server_id_list(server_list)
    request.user.save()
    logger.debug('request.user.server_list: %s', request.user.server_list)
    request.session['server_list'] = server_list
    return


def get_next_url(request):
    """
    Determine 'next' parameter
    """
    if 'next' in request.GET:
        return request.GET['next']
    if 'next' in request.POST:
        return request.POST['next']
    if 'next_url' in request.session:
        return request.session['next_url']
    return '/'
