# Generated by Django 4.2.19 on 2025-03-12 02:10

import app_core.models
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='ACCOUNT',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('status', models.CharField(help_text='active=활성, pending=승인 대기, deleted=삭제, bhide=정지', max_length=20)),
                ('note', models.TextField(blank=True, help_text='관리자 메모')),
                ('mileage', models.IntegerField(default=0, help_text='쿠폰 마일리지')),
                ('exp', models.IntegerField(default=0, help_text='레벨업 경험치')),
                ('tel', models.CharField(blank=True, help_text='연락처', max_length=20)),
                ('subsupervisor_permissions', models.CharField(blank=True, help_text='account=계정 관리 권한, post=게시글 관리 권한, coupon=쿠폰 관리 권한, message=메시지 관리 권한, banner=배너 관리 권한, setting=설정 권한)', max_length=100)),
                ('recent_ip', models.CharField(blank=True, help_text='최근 접속 IP', max_length=20)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='BANNER',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(help_text='top=상단, side=하단, post=게시글', max_length=20)),
                ('image', models.FileField(help_text='이미지', upload_to=app_core.models.upload_to)),
                ('link', models.CharField(help_text='링크', max_length=300)),
                ('status', models.CharField(help_text='full=최대 크기, half=중간 크기, none=미표시', max_length=20)),
                ('display_weight', models.IntegerField(default=0, help_text='표시 순서')),
            ],
        ),
        migrations.CreateModel(
            name='BLOCKED_IP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(help_text='차단 IP', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='BOARD',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level_cut', models.IntegerField(default=0, help_text='게시글 접근 레벨 제한')),
                ('name', models.CharField(help_text='게시판 이름', max_length=100)),
                ('board_type', models.CharField(help_text='게시판 타입', max_length=20)),
                ('display_weight', models.IntegerField(default=0, help_text='표시 순서')),
                ('comment_groups', models.ManyToManyField(help_text='댓글 작성 그룹', related_name='board_comment_groups', to='auth.group')),
                ('display_groups', models.ManyToManyField(help_text='게시판 입장 그룹', related_name='board_display_groups', to='auth.group')),
                ('parent_board', models.ForeignKey(help_text='상위 게시판', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='board_parent_board', to='app_core.board')),
                ('write_groups', models.ManyToManyField(help_text='게시글 작성 그룹', related_name='board_write_groups', to='auth.group')),
            ],
        ),
        migrations.CreateModel(
            name='CATEGORY',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='카테고리 이름', max_length=100)),
                ('display_weight', models.IntegerField(default=0, help_text='표시 순서')),
                ('parent_category', models.ForeignKey(help_text='상위 카테고리', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='category_parent_category', to='app_core.category')),
            ],
        ),
        migrations.CreateModel(
            name='COUPON',
            fields=[
                ('code', models.CharField(help_text='쿠폰 코드', max_length=20, primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='쿠폰 이름', max_length=100)),
                ('image', models.FileField(help_text='이미지', null=True, upload_to=app_core.models.upload_to)),
                ('content', models.TextField(help_text='내용', null=True)),
                ('required_mileage', models.IntegerField(default=0, help_text='필요 마일리지')),
                ('expire_at', models.DateTimeField(help_text='만료 일시')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='생성 일시')),
                ('status', models.CharField(default='active', help_text='상태(active, used, expired, deleted)', max_length=20)),
                ('note', models.TextField(help_text='관리자 메모')),
                ('create_account', models.ForeignKey(help_text='생성자', on_delete=django.db.models.deletion.CASCADE, related_name='coupon_create_account', to=settings.AUTH_USER_MODEL)),
                ('own_account', models.ForeignKey(help_text='소유 계정', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='coupon_own_account', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LEVEL_RULE',
            fields=[
                ('level', models.IntegerField(primary_key=True, serialize=False)),
                ('image', models.FileField(help_text='레벨 이미지. 이미지가 없다면, 아래 텍스트 색상과 배경 색상을 사용', null=True, upload_to=app_core.models.upload_to)),
                ('text', models.CharField(blank=True, help_text='레벨 이름. 이미지가 있다면 사용하지 않음', max_length=20)),
                ('text_color', models.CharField(blank=True, help_text='레벨 텍스트 색상. 이미지가 있다면 사용하지 않음', max_length=20)),
                ('background_color', models.CharField(blank=True, help_text='레벨 배경 색상. 이미지가 있다면 사용하지 않음', max_length=20)),
                ('required_exp', models.IntegerField(help_text='레벨업 필요 경험치')),
            ],
        ),
        migrations.CreateModel(
            name='PLACE_INFO',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location_info', models.CharField(help_text='위치 정보', max_length=100)),
                ('open_info', models.CharField(help_text='영업 정보', max_length=100)),
                ('address', models.CharField(help_text='주소', max_length=200)),
                ('ad_start_at', models.DateTimeField(auto_now_add=True, help_text='광고 시작 일시')),
                ('ad_end_at', models.DateTimeField(auto_now_add=True, help_text='광고 종료 일시')),
                ('status', models.CharField(default='hide', help_text='상태(hide, active, pending, ad)', max_length=20)),
                ('note', models.TextField(help_text='관리자 메모')),
                ('categories', models.ManyToManyField(help_text='카테고리', related_name='place_categories', to='app_core.category')),
            ],
        ),
        migrations.CreateModel(
            name='SERVER_SETTING',
            fields=[
                ('name', models.CharField(help_text='설정 이름', max_length=100, primary_key=True, serialize=False)),
                ('value', models.TextField(help_text='설정 값')),
            ],
        ),
        migrations.CreateModel(
            name='STATISTIC',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='통계 이름', max_length=100)),
                ('value', models.IntegerField(default=0, help_text='통계 값')),
                ('date', models.DateTimeField(auto_now_add=True, help_text='통계 일시')),
            ],
        ),
        migrations.CreateModel(
            name='UPLOAD',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(help_text='파일', upload_to=app_core.models.upload_to)),
            ],
        ),
        migrations.CreateModel(
            name='POST',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='제목', max_length=100)),
                ('image', models.FileField(help_text='대표 이미지', null=True, upload_to=app_core.models.upload_to)),
                ('content', models.TextField(help_text='내용', null=True)),
                ('view_count', models.IntegerField(default=0, help_text='조회수')),
                ('like_count', models.IntegerField(default=0, help_text='좋아요 수')),
                ('search_weight', models.IntegerField(default=0, help_text='검색 가중치')),
                ('hide', models.BooleanField(default=False, help_text='숨김 여부')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='작성 일시')),
                ('author', models.ForeignKey(help_text='게시글 작성자', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='post_author', to=settings.AUTH_USER_MODEL)),
                ('boards', models.ManyToManyField(help_text='게시판', related_name='post_boards', to='app_core.board')),
                ('include_coupons', models.ManyToManyField(help_text='포함된 쿠폰', related_name='post_include_coupons', to='app_core.coupon')),
                ('place_info', models.ForeignKey(help_text='여행지 정보', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='post_place_info', to='app_core.place_info')),
                ('related_post', models.ForeignKey(help_text='관련 게시글(리뷰 게시글일 경우, 리뷰 또는 쿠폰 게시글일 경우, 대상 여행지 게시글)', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='post_related_post', to='app_core.post')),
            ],
        ),
        migrations.AddField(
            model_name='place_info',
            name='post',
            field=models.ForeignKey(help_text='게시글', on_delete=django.db.models.deletion.CASCADE, related_name='place_post', to='app_core.post'),
        ),
        migrations.CreateModel(
            name='MESSAGE',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='제목', max_length=100)),
                ('image', models.FileField(help_text='이미지', null=True, upload_to=app_core.models.upload_to)),
                ('content', models.TextField(help_text='내용', null=True)),
                ('message_type', models.CharField(help_text='user_question=사용자 문의, partner_question=파트너 문의, request_ad=광고 요청, request_coupon=쿠폰 요청', max_length=20)),
                ('is_read', models.BooleanField(default=False, help_text='읽음 여부')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='생성 일시')),
                ('include_coupon', models.ForeignKey(help_text='포함된 쿠폰', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='message_include_coupon', to='app_core.coupon')),
                ('receive', models.ForeignKey(help_text='받는 사람', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='message_receive', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(help_text='보낸 사람', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='message_sender', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='coupon',
            name='related_post',
            field=models.ForeignKey(help_text='게시글', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='coupon_post', to='app_core.post'),
        ),
        migrations.CreateModel(
            name='COMMENT',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(help_text='내용')),
                ('hide', models.BooleanField(default=False, help_text='숨김 여부')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='작성 일시')),
                ('author', models.ForeignKey(help_text='작성자', on_delete=django.db.models.deletion.CASCADE, related_name='comment_author', to=settings.AUTH_USER_MODEL)),
                ('parent_comment', models.ForeignKey(help_text='상위 댓글', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comment_parent_comment', to='app_core.comment')),
                ('post', models.ForeignKey(help_text='게시글', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comment_post', to='app_core.post')),
            ],
        ),
        migrations.CreateModel(
            name='ACTIVITY',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(help_text='활동 메시지', max_length=200)),
                ('exp_change', models.IntegerField(default=0, help_text='경험치 변화')),
                ('mileage_change', models.IntegerField(default=0, help_text='마일리지 변화')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='활동 일시')),
                ('account', models.ForeignKey(help_text='계정', on_delete=django.db.models.deletion.CASCADE, related_name='activity_account', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='account',
            name='bookmarked_posts',
            field=models.ManyToManyField(help_text='즐겨찾기 여행지', related_name='account_bookmarked_places', to='app_core.post'),
        ),
        migrations.AddField(
            model_name='account',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='account',
            name='level',
            field=models.ForeignKey(help_text='사용자 레벨', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='account_level', to='app_core.level_rule'),
        ),
        migrations.AddField(
            model_name='account',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
    ]
