import logging
import requests
import urllib.parse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import HttpResponseRedirect, redirect
from django.views.decorators.http import require_http_methods
from .models import CustomUser

logger = logging.getLogger('app')


def start_oauth(request):
    """
    # View  /oauth/
    """
    request.session['login_redirect_url'] = get_next_url(request)
    logger.debug('login_redirect_url: %s', request.session['login_redirect_url'])
    params = {
        'client_id': settings.OAUTH_CLIENT_ID,
        'redirect_uri': settings.OAUTH_REDIRECT_URI,
        'response_type': 'code',
        'scope': settings.OAUTH_SCOPE,
    }
    url_params = urllib.parse.urlencode(params)
    url = 'https://discord.com/api/oauth2/authorize?{}'.format(url_params)
    return HttpResponseRedirect(url)


def oauth_callback(request):
    """
    # View  /oauth/callback/
    """
    try:
        access_token = get_access_token(request.GET['code'])
        user_profile = get_user_profile(access_token)
        user = login_user(request, user_profile['django_username'], user_profile)
        messages.info(request, f'Successfully logged in as {user.first_name}.')
    except Exception as error:
        logger.exception(error)
        messages.error(request, f'Exception during login: {error}')

    next_url = '/'
    if 'login_redirect_url' in request.session:
        next_url = request.session['login_redirect_url']
    logger.debug('next_url: %s', next_url)
    return HttpResponseRedirect(next_url)


@require_http_methods(['POST'])
def log_out(request):
    """
    View  /oauth/logout/
    """
    next_url = get_next_url(request)
    # Hack to prevent login loop when logging out on a secure page
    # This probably needs to be improved and may not work as expected
    if next_url.strip('/') in ['profile']:
        next_url = '/'
    logger.debug('next_url: %s', next_url)
    request.session['login_next_url'] = next_url
    logout(request)
    return redirect(next_url)


def login_user(request, username, profile):
    """
    Login or create user
    """
    try:
        user = CustomUser.objects.get(username=username)
    except ObjectDoesNotExist:
        user = CustomUser.objects.create_user(username)
    user = update_profile(user, profile)
    user.save()
    login(request, user)
    return user


def get_access_token(code):
    """
    Post OAuth code and Return access_token
    """
    url = '{}/oauth2/token'.format(settings.DISCORD_API_URL)
    data = {
        'client_id': settings.OAUTH_CLIENT_ID,
        'client_secret': settings.OAUTH_CLIENT_SECRET,
        'grant_type': settings.OAUTH_GRANT_TYPE,
        'redirect_uri': settings.OAUTH_REDIRECT_URI,
        'code': code,
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.post(url, data=data, headers=headers, timeout=10)
    logger.debug('status_code: %s', r.status_code)
    logger.debug('content: %s', r.content)
    return r.json()['access_token']


def get_user_profile(access_token):
    """
    Get Profile for Authenticated User
    """
    url = '{}/users/@me'.format(settings.DISCORD_API_URL)
    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
    }
    r = requests.get(url, headers=headers, timeout=10)
    logger.debug('status_code: %s', r.status_code)
    logger.debug('content: %s', r.content)
    user_profile = r.json()
    return {
        'id': user_profile['id'],
        'username': user_profile['username'],
        'discriminator': user_profile['discriminator'],
        'django_username': user_profile['username'] + user_profile['discriminator'],
        'avatar': user_profile['avatar'],
        'access_token': access_token,
    }


def update_profile(user, user_profile):
    """
    Update Django user profile with provided data
    """
    user.first_name = user_profile['username']
    user.last_name = user_profile['discriminator']
    user.discord_username = user_profile['username']
    user.discriminator = user_profile['discriminator']
    user.discord_id = user_profile['id']
    user.avatar_hash = user_profile['avatar']
    user.access_token = user_profile['access_token']
    return user


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
