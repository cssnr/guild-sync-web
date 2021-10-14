import logging
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render
from .forms import ProfileForm, ApplicantsForm
from .models import BlueProfile, BlueNews, GuildApplicants
from .tasks import notify_guild_app

logger = logging.getLogger('app')


def is_blue_member(user):
    return user.blue_team_member


def is_blue_officer(user):
    return user.blue_team_officer


def home_view(request):
    # View: /
    if request.user.is_authenticated:
        blue_profile = BlueProfile.objects.filter(
            discord_id=request.user.discord_id
        ).first()
    else:
        blue_profile = None

    live_users = BlueProfile.objects.get_live()
    if live_users:
        live_user = live_users[0]
    else:
        live_user = None

    blue_news = BlueNews.objects.all().order_by('-pk')[:2]

    data = {
        'blue_profile': blue_profile,
        'blue_news': blue_news,
        'live_user': live_user,
    }
    return render(request, 'home.html', data)


def news_view(request):
    # View: /roster/
    blue_news = BlueNews.objects.all().order_by('-pk')[:50]
    return render(request, 'news.html', {'blue_news': blue_news})


def roster_view(request):
    # View: /roster/
    guild_roster = BlueProfile.objects.all().order_by('created_at')
    return render(request, 'roster.html', {'guild_roster': guild_roster})


@login_required
@user_passes_test(is_blue_member, login_url='/')
def profile_view(request):
    # View: /profile/
    if not request.method == 'POST':
        blue_profile = BlueProfile.objects.filter(
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
                blue_profile, created = BlueProfile.objects.get_or_create(
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


def apply_view(request):
    # View: /apply/
    if not request.method == 'POST':
        return render(request, 'apply.html')
    else:
        logger.debug(request.POST)
        form = ApplicantsForm(request.POST)
        if form.is_valid():
            if not google_verify(request):
                data = {'err_msg': 'Google CAPTCHA not verified.'}
                return JsonResponse(data, status=400)
            new_app = GuildApplicants(
                char_name=form.cleaned_data['char_name'],
                char_role=form.cleaned_data['char_role'],
                warcraft_logs=form.cleaned_data['warcraft_logs'],
                speed_test=form.cleaned_data['speed_test'],
                spoken_langs=form.cleaned_data['spoken_langs'],
                native_lang=form.cleaned_data['native_lang'],
                fri_raid=form.cleaned_data['fri_raid'],
                sat_raid=form.cleaned_data['sat_raid'],
                tue_raid=form.cleaned_data['tue_raid'],
                raid_exp=form.cleaned_data['raid_exp'],
                why_blue=form.cleaned_data['why_blue'],
                contact_info=form.cleaned_data['contact_info'],
            )
            new_app.save()
            request.session['application_submitted'] = True
            logger.debug('new_app.id: %s', new_app.id)
            notify_guild_app.delay(new_app.id)
            return JsonResponse({}, status=200)
        else:
            return JsonResponse(form.errors, status=400)


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
