import logging
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import HttpResponseRedirect, render
from django.urls import reverse
from .forms import ServerForm
from .models import ServerProfile

logger = logging.getLogger('app')


def is_auth_user(user):
    return user.is_authenticated


def home_view(request):
    """
    # View  /
    """
    if 'server_list' not in request.session and request.user.is_authenticated:
        server_list = get_user_servers(request.user.access_token)
        if isinstance(server_list, requests.models.Response):
            logger.error(server_list.content)
            messages.warning(request, 'Error getting server list from Discord API.')
            return render(request, 'home.html')
        request.session['server_list'] = server_list
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
def server_view(request, serverid):
    """
    # View  /server/{serverid}
    """
    if not request.method == 'POST':
        extra_data = {}
        server_profile = ServerProfile.objects.filter(server_id=serverid).first()
        logger.debug('server_profile: %s', server_profile)
        server_profile = {} if not server_profile else server_profile
        logger.debug('server_profile: %s', server_profile)
        server_data = get_server_by_id(request, serverid)
        logger.debug(server_data)
        data = {'server_data': server_data, 'server_profile': server_profile}
        if server_profile and server_profile.is_enabled:
            # serer enabled
            extra_data = cache.get(serverid)
            logger.debug('CACHE RESPONSE: %s', extra_data)
            if not extra_data:
                roles = get_guild_roles(serverid)
                if isinstance(roles, requests.models.Response):
                    logger.error(roles.content)
                    if roles.status_code == 403:
                        server_profile.is_enabled = False
                        server_profile.save()
                        messages.warning(request, 'Bot has been removed from server.')
                        return render(request, 'server.html')
                    else:
                        messages.warning(request, 'Discord API error. Try again later.')
                        return render(request, 'server.html')

                channels = get_guild_channels(serverid)
                if isinstance(channels, requests.models.Response):
                    logger.error(channels.content)
                    if channels.status_code == 403:
                        server_profile.is_enabled = False
                        server_profile.save()
                        messages.warning(request, 'Bot has been removed from server.')
                        return render(request, 'server.html')
                    else:
                        messages.warning(request, 'Discord API error. Try again later.')
                        return render(request, 'server.html')

                extra_data = {'roles': roles, 'channels': channels}
                logger.info('extra_data: %s', extra_data)
                cache.set(serverid, extra_data, 30)
        logger.info('extra_data: %s', extra_data)
        data.update(extra_data)
        request.session['last_server'] = serverid
        return render(request, 'server.html', data)

    try:
        logger.debug(request.POST)
        form = ServerForm(request.POST)
        logger.debug('1')
        if form.is_valid():
            logger.debug('2')
            server_data = get_server_by_id(request, serverid)
            server_profile, created = ServerProfile.objects.get_or_create(server_id=serverid)
            server_profile.server_name = server_data['name']
            server_profile.guild_name = form.cleaned_data['guild_name']
            server_profile.guild_realm = form.cleaned_data['guild_realm']
            server_profile.guild_role = form.cleaned_data['guild_role']
            server_profile.alert_channel = form.cleaned_data['alert_channel']
            server_profile.server_notes = form.cleaned_data['server_notes']
            server_profile.sync_classes = bool(form.cleaned_data['sync_classes'])
            server_profile.save()
            logger.debug('server_profile: save')
            return JsonResponse({}, status=200)
        else:
            logger.debug('3')
            return JsonResponse(form.errors, status=400)
    except Exception as error:
        logger.debug('4')
        logger.warning(error)
        logger.exception(error)
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


def get_user_servers(access_token):
    url = '{}/users/@me/guilds'.format(settings.DISCORD_API_URL)
    r = discord_api_call(url, access_token, tt='Bearer')
    if not r.ok:
        return r
    server_list = []
    for server in r.json():
        if server['permissions'] == 2147483647:
            server_list.append(server)
    logger.debug(server_list)
    return server_list


def get_guild_roles(serverid):
    url = '{}/guilds/{}/roles'.format(settings.DISCORD_API_URL, serverid)
    r = discord_api_call(url, settings.DISCORD_BOT_TOKEN)
    if not r.ok:
        return r
    role_list = []
    for role in r.json():
        if not role['managed'] and not role['position'] == 0:
            role_list.append((role['name'], role['id']))
    logger.debug(role_list)
    return role_list


def get_guild_channels(serverid):
    url = '{}/guilds/{}/channels'.format(settings.DISCORD_API_URL, serverid)
    r = discord_api_call(url, settings.DISCORD_BOT_TOKEN)
    if not r.ok:
        return r
    channels_list = []
    for channel in r.json():
        if channel['type'] == 0:
            channels_list.append((channel['name'], channel['id']))
    logger.debug(channels_list)
    return channels_list


def get_server_by_id(request, serverid):
    for server in request.session['server_list']:
        if server['id'] == serverid:
            logger.debug('Matched server: %s', server['id'])
            return server
    logger.warning('NO Matching Servers!')
    return None


def discord_api_call(url, token, tt='Bot'):
    logger.info('discord_api_call')
    headers = {'Authorization': '{} {}'.format(tt, token)}
    return requests.get(url, headers=headers, timeout=6)
    # if not r.ok:
    #     r.raise_for_status()
    # j = r.json()
    # logger.debug(j)
    # return j


# def check_guild_user(serverid, userid):
#     url = '{}/guilds/{}/members/{}'.format(
#         settings.DISCORD_API_URL,
#         serverid, userid,
#     )
#     headers = {
#         'Authorization': 'Bot {}'.format(settings.DISCORD_BOT_TOKEN),
#     }
#     logger.debug('API CALL')
#     r = requests.get(url, headers=headers, timeout=6)
#     if not r.ok:
#         logger.debug('r.status_code: %s', r.status_code)
#         logger.debug('r.content: %s', r.content)
#         return False
#     return True
