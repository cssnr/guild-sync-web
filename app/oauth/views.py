import logging
import requests
import urllib.parse
from django.contrib.auth import login, logout
# from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.shortcuts import HttpResponseRedirect, HttpResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .models import CustomUser

logger = logging.getLogger('app')


def do_oauth(request):
    """
    # View  /oauth/
    """
    request.session['login_redirect_url'] = get_next_url(request)
    params = {
        'client_id': settings.DISCORD_CLIENT_ID,
        'redirect_uri': settings.DISCORD_REDIRECT_URI,
        'response_type': 'code',
        'scope': settings.DISCORD_SCOPE,
    }
    url_params = urllib.parse.urlencode(params)
    url = 'https://discord.com/api/oauth2/authorize?{}'.format(url_params)
    return HttpResponseRedirect(url)


def callback(request):
    """
    # View  /oauth/callback/
    """
    try:
        oauth_code = request.GET['code']
        access_token = get_access_token(oauth_code)
        user_profile = get_user_profile(access_token)
        auth = login_user(request, user_profile)
        if not auth:
            err_msg = 'Unable to complete login process. Report as a Bug.'
            return HttpResponse(err_msg, content_type='text/plain')
        try:
            next_url = request.session['login_redirect_url']
        except Exception:
            next_url = '/'
        return HttpResponseRedirect(next_url)

    except Exception as error:
        logger.exception(error)
        err_msg = 'Fatal Login Error. Report as Bug: %s' % error
        return HttpResponse(err_msg, content_type='text/plain')


@require_http_methods(['POST'])
def log_out(request):
    """
    View  /oauth/logout/
    """
    next_url = get_next_url(request)

    # Hack to prevent login loop when logging out on a secure page
    if next_url.strip('/') in ['profile']:
        next_url = '/'
    logger.debug('next_url: %s', next_url)

    request.session['login_next_url'] = next_url
    logout(request)
    return redirect(next_url)


def login_user(request, user_profile):
    """
    Login or Create New User
    """
    try:
        user = CustomUser.objects.get(username=user_profile['django_username'])
        user = update_profile(user, user_profile)
        user.save()
        login(request, user)
        return True
    except ObjectDoesNotExist:
        user = CustomUser.objects.create_user(user_profile['django_username'])
        user = update_profile(user, user_profile)
        user.save()
        login(request, user)
        return True
    except Exception as error:
        logger.exception(error)
        return False


def get_access_token(code):
    """
    Post OAuth code and Return access_token
    """
    url = '{}/oauth2/token'.format(settings.DISCORD_API_URL)
    data = {
        'client_id': settings.DISCORD_CLIENT_ID,
        'client_secret': settings.DISCORD_CLIENT_SECRET,
        'grant_type': settings.DISCORD_GRANT_TYPE,
        'redirect_uri': settings.DISCORD_REDIRECT_URI,
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

    # url = '{}/guilds/{}/members/{}'.format(
    #     settings.DISCORD_API_URL,
    #     settings.BLUE_DISCORD_ID,
    #     user_profile['id'],
    # )
    # headers = {
    #     'Authorization': 'Bot {}'.format(settings.BLUE_DISCORD_BOT_TOKEN),
    # }
    # r = requests.get(url, headers=headers, timeout=10)
    # logger.debug('status_code: %s', r.status_code)
    # logger.debug('content: %s', r.content)
    # user_guild = r.json()

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

    # officers = Group.objects.get(name='Officers')
    # logger.debug('blue_team_officer: %s', user_profile['blue_team_officer'])
    # if user_profile['blue_team_officer']:
    #     officers.user_set.add(user)
    # else:
    #     officers.user_set.remove(user)

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
    Determine 'next' Parameter
    """
    try:
        next_url = request.GET['next']
    except Exception:
        try:
            next_url = request.POST['next']
        except Exception:
            try:
                next_url = request.session['login_next_url']
            except Exception:
                next_url = '/'
    if not next_url:
        next_url = '/'
    return next_url
