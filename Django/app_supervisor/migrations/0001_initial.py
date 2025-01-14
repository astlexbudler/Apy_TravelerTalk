# Generated by Django 4.2.3 on 2025-01-15 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BANNER',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('location', models.CharField(help_text='배너 위치(top, side)', max_length=20)),
                ('display_order', models.IntegerField(help_text='배너 표시 순서(숫가가 클수록 먼저 표시)')),
                ('image', models.CharField(help_text='배너 이미지 URL', max_length=200)),
                ('link', models.CharField(help_text='배너 링크 URL', max_length=200)),
                ('clicks', models.TextField(blank=True, help_text='클릭한 사용자 ID(없으면 공백. ,로 구분)', null=True)),
                ('created_dt', models.DateTimeField(auto_now_add=True, help_text='생성일시')),
            ],
        ),
    ]
