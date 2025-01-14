# Generated by Django 4.2.3 on 2025-01-15 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='COUPON',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('code', models.CharField(help_text='쿠폰 코드', max_length=20)),
                ('create_account_id', models.CharField(help_text='쿠폰 생성자 ID(파트너 또는 관리자 ID)', max_length=60)),
                ('own_user_id', models.CharField(help_text='쿠폰 소유자 ID', max_length=60)),
                ('name', models.CharField(help_text='쿠폰 이름(최대 100자)', max_length=100)),
                ('description', models.TextField(help_text='쿠폰 설명')),
                ('images', models.TextField(blank=True, help_text='쿠폰 이미지 URL(없으면 공백. ,로 구분)', null=True)),
                ('post_id', models.CharField(blank=True, help_text='관련 게시물 ID. 없으면 공백', max_length=16, null=True)),
                ('created_dt', models.DateTimeField(auto_now_add=True, help_text='생성일시')),
                ('required_point', models.IntegerField(help_text='필요 포인트')),
            ],
        ),
        migrations.CreateModel(
            name='COUPON_HISTORY',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('code', models.CharField(help_text='쿠폰 코드', max_length=20)),
                ('create_account_id', models.CharField(help_text='쿠폰 생성자 ID(파트너 또는 관리자 ID)', max_length=60)),
                ('used_user_id', models.CharField(help_text='쿠폰 사용자 ID', max_length=60)),
                ('name', models.CharField(help_text='쿠폰 이름(최대 100자)', max_length=100)),
                ('description', models.TextField(help_text='쿠폰 설명')),
                ('images', models.TextField(blank=True, help_text='쿠폰 이미지 URL(없으면 공백. ,로 구분)', null=True)),
                ('post_id', models.CharField(blank=True, help_text='관련 게시물 ID. 없으면 공백', max_length=16, null=True)),
                ('created_dt', models.DateTimeField(help_text='생성일시')),
                ('used_dt', models.DateTimeField(auto_now_add=True, help_text='사용일시')),
                ('required_point', models.IntegerField(help_text='필요 포인트')),
                ('status', models.CharField(help_text='쿠폰 상태(used, expired, deleted)', max_length=30)),
                ('note', models.TextField(blank=True, help_text='관리자 또는 파트너 메모', null=True)),
            ],
        ),
    ]
