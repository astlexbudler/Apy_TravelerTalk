# Generated by Django 4.2.3 on 2025-01-15 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MESSAGE',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('sender_id', models.CharField(help_text='보낸 사람 ID(관리자일경우 supervisor)', max_length=60)),
                ('receiver_id', models.CharField(help_text='받는 사람 ID(관리자일경우 supervisor)', max_length=60)),
                ('title', models.CharField(help_text='제목(최대 100자)', max_length=100)),
                ('content', models.TextField(help_text='내용')),
                ('send_dt', models.DateTimeField(auto_now_add=True, help_text='보낸 일시')),
                ('read_dt', models.DateTimeField(blank=True, help_text='읽은 일시(읽지 않았으면 공백)', null=True)),
                ('include_coupon', models.CharField(blank=True, help_text='포함된 쿠폰 코드(없으면 공백)', max_length=20, null=True)),
                ('images', models.TextField(blank=True, help_text='이미지 URL(없으면 공백. ,로 구분)', null=True)),
            ],
        ),
    ]