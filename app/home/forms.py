from django import forms


class ServerForm(forms.Form):
    guild_name = forms.CharField(max_length=64)
    guild_realm = forms.CharField(max_length=32)
    guild_role = forms.CharField(max_length=32)
    alert_channel = forms.CharField(max_length=32, required=False)
    server_notes = forms.CharField(required=False)
    sync_classes = forms.BooleanField(required=False)
