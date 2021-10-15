import logging
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render
from .forms import ProfileForm
from .models import ServerProfile

logger = logging.getLogger('app')


def is_blue_member(user):
    return user.is_authenticated


def home_view(request):
    # View: /
    discord_profile = None
    data = {
        'discord_profile': discord_profile,
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
        # server_profile = ServerProfile.objects.filter(
        #     server_id=request.user.discord_id
        # ).first()
        # test
        server_profile = {}
        server_profile = {} if not server_profile else server_profile
        data = {'blue_profile': server_profile}
        return render(request, 'profile.html', data)

    else:
        try:
            logger.debug(request.POST)
            form = ProfileForm(request.POST)
            if form.is_valid():
                raise Exception('WIP')
                blue_profile, created = ServerProfile.objects.get_or_create(
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
