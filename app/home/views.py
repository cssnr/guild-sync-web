import logging
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import HttpResponseRedirect, render
from django.urls import reverse
from .forms import ProfileForm
from .models import UserProfile, ServerProfile

logger = logging.getLogger('app')


def is_auth_user(user):
    return user.is_authenticated


def home_view(request):
    """
    # View  /
    """
    if 'server_list' not in request.session and request.user.is_authenticated:
        request.session['server_list'] = get_discord_servers(request.user)
    if 'server_list' in request.session:
        logger.debug('server_list: from session')
        data = {'server_list': request.session['server_list']}
    else:
        data = {}
    return render(request, 'home.html', data)


def news_view(request):
    """
    # View  /news/
    """
    return render(request, 'news.html')


@login_required
@user_passes_test(is_auth_user, login_url='/')
def profile_view(request):
    """
    # View  /profile/
    """
    if not request.method == 'POST':
        blue_profile = UserProfile.objects.filter(
            discord_id=request.user.discord_id
        ).first()
        blue_profile = {} if not blue_profile else blue_profile
        data = {'blue_profile': blue_profile}
        return render(request, 'profile.html', data)

    try:
        logger.debug(request.POST)
        form = ProfileForm(request.POST)
        if form.is_valid():
            blue_profile, created = UserProfile.objects.get_or_create(discord_id=request.user.discord_id)
            blue_profile.main_char = form.cleaned_data['main_char']
            blue_profile.main_class = form.cleaned_data['main_class']
            blue_profile.main_role = form.cleaned_data['main_role']
            blue_profile.user_description = form.cleaned_data['user_description']
            blue_profile.twitch_username = form.cleaned_data['twitch_username']
            blue_profile.show_in_roster = bool(form.cleaned_data['show_in_roster'])
            blue_profile.save()
            return JsonResponse({}, status=200)
        else:
            return JsonResponse(form.errors, status=400)
    except Exception as error:
        logger.warning(error)
        return JsonResponse({'err_msg': str(error)}, status=400)


@login_required
@user_passes_test(is_auth_user, login_url='/')
def server_view(request, serverid):
    """
    # View  /server/{serverid}
    """
    if not request.method == 'POST':
        server_profile = ServerProfile.objects.filter(server_id=serverid).first()
        server_profile = {} if not server_profile else server_profile
        server_data = get_server_by_id(request, serverid)
        logger.debug(server_data)
        if server_profile and server_profile.is_enabled:
            enabled = cache.get(serverid)
            logger.debug('CACHE RESPONSE: %s', enabled)
            if enabled is None:
                enabled = check_guild_user(serverid, settings.DISCORD_BOT_USER_ID)
                cache.set(serverid, enabled, 15)
            if not enabled:
                server_profile.is_enabled = False
                server_profile.save()
                messages.warning(request, 'Bot has been removed from server and must be re-enabled.')
        data = {'server_data': server_data, 'server_profile': server_profile}
        request.session['last_server'] = serverid
        return render(request, 'server.html', data)

    try:
        logger.debug(request.POST)
        return JsonResponse({}, status=400)
    except Exception as error:
        logger.warning(error)
        return JsonResponse({'err_msg': str(error)}, status=400)


def callback_view(request):
    """
    # View  /callback/
    """
    try:
        if 'code' in request.GET and 'guild_id' in request.GET:
            # bot added successfully
            logger.debug('code: %s', request.GET['code'])
            guild_id = request.GET['guild_id']
            logger.debug('guild_id: %s', guild_id)

            server_profile, created = ServerProfile.objects.get_or_create(server_id=guild_id)
            server_profile.is_enabled = True
            server_profile.save()

            messages.success(request, 'Bot successfully added to server.')

            r_url = reverse('home:server', kwargs={'serverid': guild_id})
            logger.debug('r_url: %s', r_url)
            return HttpResponseRedirect(r_url)

        if 'error' in request.GET:
            # known error adding bot
            logger.warning(request.GET['error'])
            logger.warning(request.GET['error_description'])
            messages.error(request, '{}: {}'.format(request.GET['error'], request.GET['error_description']))
        else:
            # unknown error adding bot
            logger.error('Error: unknown callback response.')
            messages.error(request, 'Error: unknown callback response.')
        r_url = reverse('home:server', kwargs={'serverid': request.session['last_server']})
        logger.debug('r_url: %s', r_url)
        return HttpResponseRedirect(r_url)

    except Exception as error:
        logger.exception(error)
        messages.error(request, 'Unknown Fatal Error!')
        return HttpResponseRedirect('/')


def get_discord_servers(user):
    url = '{}/users/@me/guilds'.format(settings.DISCORD_API_URL)
    headers = {
        'Authorization':  'Bearer {}'.format(user.access_token),
    }
    logger.debug('API CALL')
    r = requests.get(url, headers=headers, timeout=6)
    if not r.ok:
        r.raise_for_status()
    j = r.json()
    logger.debug(j)
    server_list = []
    for server in j:
        if server['permissions'] == 2147483647:
            server_list.append(server)
    logger.debug(server_list)
    return server_list


def check_guild_user(serverid, userid):
    url = '{}/guilds/{}/members/{}'.format(
        settings.DISCORD_API_URL,
        serverid, userid,
    )
    headers = {
        'Authorization': 'Bot {}'.format(settings.DISCORD_BOT_TOKEN),
    }
    logger.debug('API CALL')
    r = requests.get(url, headers=headers, timeout=10)
    if not r.ok:
        logger.debug('r.status_code: %s', r.status_code)
        logger.debug('r.content: %s', r.content)
        return False
    return True


def get_server_by_id(request, serverid):
    for server in request.session['server_list']:
        if server['id'] == serverid:
            logger.debug('Matched server: %s', server['id'])
            return server
    logger.warning('NO Matching Servers!')
    return None
