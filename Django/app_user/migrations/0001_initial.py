# Generated by Django 4.2.3 on 2025-01-21 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ACTIVITY',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.CharField(help_text='사용자 ID', max_length=60)),
                ('location', models.CharField(blank=True, help_text='활동 위치(없으면 공백)', max_length=200, null=True)),
                ('message', models.TextField(help_text='활동 내용')),
                ('point_change', models.CharField(blank=True, help_text='포인트 변동량', max_length=20, null=True)),
                ('created_dt', models.DateTimeField(auto_now_add=True, help_text='활동 일시')),
            ],
        ),
    ]
