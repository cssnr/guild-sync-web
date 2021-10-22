# Generated by Django 3.2.8 on 2021-10-22 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ServerProfile',
            fields=[
                ('server_id', models.CharField(max_length=32, primary_key=True, serialize=False, verbose_name='Discord Server ID')),
                ('server_name', models.CharField(blank=True, max_length=32, verbose_name='Discord Server Name')),
                ('guild_name', models.CharField(blank=True, max_length=64, verbose_name='WoW Guild Name')),
                ('guild_realm', models.CharField(blank=True, max_length=32, verbose_name='WoW Guild Realm')),
                ('guild_role', models.CharField(blank=True, max_length=32, verbose_name='Discord Guild Role')),
                ('alert_channel', models.CharField(blank=True, max_length=32, verbose_name='Discord Alerts Channel')),
                ('server_notes', models.TextField(blank=True, verbose_name='Server Notes')),
                ('sync_method', models.CharField(default=False, max_length=32, verbose_name='Sync Method')),
                ('sync_classes', models.BooleanField(default=False, verbose_name='Sync Class Roles')),
                ('create_roles', models.BooleanField(default=False, verbose_name='Create Class Roles')),
                ('is_enabled', models.BooleanField(default=False, verbose_name='Server Enable Status')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Server Profile',
                'verbose_name_plural': 'Server Profiles',
            },
        ),
    ]
