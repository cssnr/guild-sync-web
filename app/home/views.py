import logging
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render
from .forms import ProfileForm
from .models import UserProfile, ServerProfile

logger = logging.getLogger('app')


def is_blue_member(user):
    return user.is_authenticated


def home_view(request):
    # View: /
    if 'server_list' not in request.session:
        request.session['server_list'] = get_discord_servers(request.user)
    data = {
        'server_list': request.session['server_list'],
    }
    return render(request, 'home.html', data)


def news_view(request):
    # View: /news/
    return render(request, 'news.html')


@login_required
@user_passes_test(is_blue_member, login_url='/')
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


def get_discord_servers(user):
    url = '{}/users/@me/guilds'.format(settings.DISCORD_API_URL)
    headers = {
        'Authorization':  'Bearer {}'.format(user.access_token),
    }
    r = requests.get(url, headers=headers, timeout=6)
    j = r.json()
    logger.debug(j)
    if not r.ok:
        r.raise_for_status()
    server_list = []
    for server in j:
        if server['permissions'] == 2147483647:
            server_list.append(server)
    logger.debug(server_list)
    return server_list


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
