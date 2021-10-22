import json
import logging
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .forms import ServerForm
from .models import ServerProfile
from .tasks import process_upload, discord_api_call, get_guild_roles
from oauth.models import CustomUser

logger = logging.getLogger('app')


def is_auth_user(user):
    return user.is_authenticated


def home_view(request):
    """
    # View  /
    """
    if request.user.is_authenticated:
        data = {'server_list': request.session['server_list']}
        return render(request, 'home.html', data)
    else:
        return render(request, 'home.html')


def about_view(request):
    """
    # View  /about/
    """
    return render(request, 'about.html')


@login_required
@user_passes_test(is_auth_user, login_url='/')
def server_view(request, serverid):
    """
    # View  /server/{serverid}
    """
    if not request.method == 'POST':
        request.session['last_server'] = serverid
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
                        return render(request, 'server.html', data)
                    else:
                        messages.warning(request, 'Discord API error. Try again later.')
                        return render(request, 'server.html', data)

                channels = get_guild_channels(serverid)
                if isinstance(channels, requests.models.Response):
                    logger.error(channels.content)
                    if channels.status_code == 403:
                        server_profile.is_enabled = False
                        server_profile.save()
                        messages.warning(request, 'Bot has been removed from server.')
                        return render(request, 'server.html', data)
                    else:
                        messages.warning(request, 'Discord API error. Try again later.')
                        return render(request, 'server.html', data)

                extra_data = {'roles': roles, 'channels': channels}
                logger.info('extra_data: %s', extra_data)
                cache.set(serverid, extra_data, 30)
        logger.info('extra_data: %s', extra_data)
        data.update(extra_data)
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
            server_profile.create_roles = bool(form.cleaned_data['create_roles'])
            server_profile.sync_method = form.cleaned_data['sync_method'][0]
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
            messages.error(request, f"{request.GET['error']}: {request.GET['error_description']}")
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


@csrf_exempt
@require_http_methods(['POST'])
def client_auth(request):
    """
    # View  /auth/
    """
    try:
        access_key = request.headers['Access-Key']
        user = CustomUser.objects.get(access_key=access_key)
        return HttpResponse('Logged in as: %s' % user.username)
    except Exception as error:
        logger.info(error)
        return HttpResponse('auth-fail')


@csrf_exempt
@require_http_methods(['POST'])
def client_upload(request):
    """
    # View  /upload/
    """
    try:
        access_key = request.headers['Access-Key']
        user = CustomUser.objects.get(access_key=access_key)
        data = json.loads(request.body)
        # logger.debug(data)
        process_upload.delay(user.pk, data)

        return HttpResponse('success')
    except Exception as error:
        logger.info(error)
        return HttpResponse('auth-fail')


def get_user_servers(access_token):
    url = f'{settings.DISCORD_API_URL}/users/@me/guilds'
    r = discord_api_call(url, access_token, tt='Bearer')
    if not r.ok:
        return r
    server_list = []
    for server in r.json():
        if server['permissions'] == 2147483647:
            server_list.append(server)
    logger.debug(server_list)
    return server_list


def get_guild_channels(serverid):
    url = f'{settings.DISCORD_API_URL}/guilds/{serverid}/channels'
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


def get_server_id_list(server_list):
    server_id_list = []
    for server in server_list:
        server_id_list.append(server['id'])
    return server_id_list


# def check_guild_user(serverid, userid):
#     url = f'{settings.DISCORD_API_URL}/guilds/{serverid}/members/{userid}'
#     headers = {'Authorization': f'Bot {settings.DISCORD_BOT_TOKEN}'}
#     logger.debug('API CALL')
#     r = requests.get(url, headers=headers, timeout=6)
#     if not r.ok:
#         logger.debug('r.status_code: %s', r.status_code)
#         logger.debug('r.content: %s', r.content)
#         return False
#     return True
