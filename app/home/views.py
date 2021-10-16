import logging
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render
from .forms import ProfileForm
from .models import UserProfile, ServerProfile

logger = logging.getLogger('app')


def is_auth_user(user):
    return user.is_authenticated


def home_view(request):
    # View: /
    if 'server_list' not in request.session and request.user.is_authenticated:
        request.session['server_list'] = get_discord_servers(request.user)
    if 'server_list' in request.session:
        data = {'server_list': request.session['server_list']}
    else:
        data = {}
    return render(request, 'home.html', data)


def news_view(request):
    # View: /news/
    return render(request, 'news.html')


@login_required
@user_passes_test(is_auth_user, login_url='/')
def profile_view(request):
    # View: /profile/
    if not request.method == 'POST':
        blue_profile = UserProfile.objects.filter(
            discord_id=request.user.discord_id
        ).first()
        blue_profile = {} if not blue_profile else blue_profile
        data = {'blue_profile': blue_profile}
        return render(request, 'profile.html', data)

    else:
        try:
            logger.debug(request.POST)
            form = ProfileForm(request.POST)
            if form.is_valid():
                blue_profile, created = UserProfile.objects.get_or_create(
                    discord_id=request.user.discord_id)
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
    # View: /server/{serverid}/
    if not request.method == 'POST':
        server_profile = ServerProfile.objects.filter(server_id=serverid).first()
        server_profile = {} if not server_profile else server_profile
        server_data = get_server_by_id(request, serverid)
        logger.debug(server_data)
        logger.debug(type(server_data))
        data = {'server_data': server_data, 'server_profile': server_profile}
        return render(request, 'server.html', data)

    else:
        try:
            logger.debug(request.POST)
            return JsonResponse({}, status=400)
        except Exception as error:
            logger.warning(error)
            return JsonResponse({'err_msg': str(error)}, status=400)


def get_discord_servers(user):
    url = '{}/users/@me/guilds'.format(settings.DISCORD_API_URL)
    headers = {
        'Authorization':  'Bearer {}'.format(user.access_token),
    }
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


def get_server_by_id(request, serverid):
    for server in request.session['server_list']:
        logger.debug('Checking server: %s' % server['id'])
        if server['id'] == serverid:
            logger.debug('Matched server: %s' % server['id'])
            return server
    logger.warning('NO Matching Servers!')
    return None


def google_verify(request):
    if 'gverified' in request.session and request.session['gverified']:
        return True
    try:
        url = 'https://www.google.com/recaptcha/api/siteverify'
        data = {
            'secret': settings.GOOGLE_SITE_SECRET,
            'response': request.POST['g-recaptcha-response']
        }
        r = requests.post(url, data=data, timeout=6)
        j = r.json()
        logger.debug(j)
        if j['success']:
            request.session['gverified'] = True
            return True
        else:
            return False
    except Exception as error:
        logger.exception(error)
        return False
