from django import forms


class ProfileForm(forms.Form):
    main_char = forms.CharField(max_length=32)
    main_class = forms.CharField(max_length=32)
    main_role = forms.CharField(max_length=32)
    user_description = forms.CharField(required=False)
    twitch_username = forms.CharField(max_length=32, required=False)
    show_in_roster = forms.BooleanField(required=False)


class NewsForm(forms.Form):
    title = forms.CharField(max_length=64)
    display_name = forms.CharField(max_length=32)
    description = forms.CharField()


class ApplicantsForm(forms.Form):
    char_name = forms.CharField(max_length=32)
    char_role = forms.CharField(max_length=32)
    warcraft_logs = forms.URLField()
    speed_test = forms.URLField()
    spoken_langs = forms.CharField(max_length=32)
    native_lang = forms.CharField(max_length=32)
    fri_raid = forms.BooleanField(required=False)
    sat_raid = forms.BooleanField(required=False)
    tue_raid = forms.BooleanField(required=False)
    raid_exp = forms.CharField()
    why_blue = forms.CharField()
    contact_info = forms.CharField(max_length=128)
