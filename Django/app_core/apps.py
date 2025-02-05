from datetime import timedelta
from django.apps import AppConfig
from apptoaster import settings

class AppCoreConfig(AppConfig):
  default_auto_field = 'django.db.models.BigAutoField'
  name = 'app_core'

  def ready(self):

    if settings.SCHEDULER_DEFAULT:
        from . import scheduler
        scheduler.startScheduler()

    try:
      from django.contrib.auth import get_user_model
      from datetime import datetime
      from django.contrib.auth.models import Group
      from . import models

      # 서버 초기 데이터 구성
      # 만약, 초기 데이터가 설정되어있지 않을 경우, 데이터 생성
      is_SERVER_SETTING_exist = models.SERVER_SETTING.objects.all().count() > 0
      if not is_SERVER_SETTING_exist: # 초기 데이터가 없을 경우

        print('데이터베이스 기본 데이터 생성 시작')

        # SERVER_SETTING: 서버 설정 테이블
        models.SERVER_SETTING.objects.create(
          name='service_name', # 서비스명
          value='여행자들의 대화'
        )
        models.SERVER_SETTING.objects.create(
          name='site_logo', # 로고
          value='/media/icon.png'
        )
        models.SERVER_SETTING.objects.create(
          name='site_header', # 로고
          value='/media/header-image.jpg'
        )
        models.SERVER_SETTING.objects.create(
          name='company_info', # 회사 정보
          value='<p>관리자 페이지에서 회사 정보를 입력해주세요.</p>'
        )
        models.SERVER_SETTING.objects.create(
          name='social_network', # X 주소
          value='https://www.x.com'
        )
        models.SERVER_SETTING.objects.create(
          name='terms', # 이용약관
          value='관리자 페이지에서 이용약관을 입력해주세요.'
        )
        models.SERVER_SETTING.objects.create(
          name='register_point', # 가입 시 제공 포인트
          value='1000'
        )
        models.SERVER_SETTING.objects.create(
          name='attend_point', # 출석 시 제공 포인트
          value='100'
        )
        models.SERVER_SETTING.objects.create(
          name='post_point', # 게시물 작성 시 제공 포인트
          value='100'
        )
        models.SERVER_SETTING.objects.create(
          name='review_point', # 후기 게시물 작성 시 제공 포인트
          value='200'
        )
        models.SERVER_SETTING.objects.create(
          name='comment_point', # 댓글 작성 시 제공 포인트
          value='50'
        )

        # LEVEL_RULE: 레벨 규칙 테이블
        models.LEVEL_RULE.objects.create(
          level=1, # 레벨
          text='1레벨', # 레벨 이름
          text_color='#000000', # 레벨 텍스트 색상
          background_color='#cd7f32', # 레벨 배경 색상
          required_exp=0 # 레벨업 포인트
        )
        models.LEVEL_RULE.objects.create(
          level=2, # 레벨
          text='2레벨', # 레벨 이름
          text_color='#000000', # 레벨 텍스트 색상
          background_color='#cd7f32', # 레벨 배경 색상
          required_exp=100 # 레벨업 포인트
        )

        # GROUP: 그룹 테이블
        guest_group = Group.objects.create(
          name='guest' # 게스트 그룹
        )
        user_group = Group.objects.create(
          name='user' # 사용자 그룹
        )
        dame_group = Group.objects.create(
          name='dame' # Dame 그룹
        )
        partner_group = Group.objects.create(
          name='partner' # 파트너 그룹
        )
        subsupervisor_group = Group.objects.create(
          name='subsupervisor' # 부관리자 그룹
        )
        supervisor_group = Group.objects.create(
          name='supervisor' # 사이트 관리자 그룹
        )
        admin_group = Group.objects.create(
          name='admin' # 데이터베이스 관리자 그룹
        )

        # ACCOUNT: 계정 테이블
        supervisor = models.ACCOUNT(
          username='supervisor', # 관리자 아이디
          first_name='관리자', # 닉네임
          last_name='',
          email='',
          status = 'active', # 계정 상태
          note='',
          tel='', # 연락처
          subsupervisor_permissions='', # 부관리자 권한
        )
        supervisor.set_password('supervisor1!')
        supervisor.save()
        supervisor.groups.add(supervisor_group)
        supervisor.save()

        admin = models.ACCOUNT(
          username='admin', # 관리자 아이디
          email='applify.kr@gmail.com',
          is_staff=True,
          is_superuser=True,
        )
        admin.set_password('admin1!')
        admin.save()
        admin.groups.add(admin_group)
        admin.save()

        # CATEGORY: 카테고리 테이블
        abroad = models.CATEGORY.objects.create(
          name='국내'
        )

        # BOARD: 게시판 테이블
        # 출석체크 게시판
        attend = models.BOARD.objects.create(
          name='출석체크',
          board_type='attendance',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - none
        # comment_groups - all
        attend.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        attend.enter_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        attend.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        attend.save()

        # 가입인사 게시판
        hello = models.BOARD.objects.create(
          name='가입인사',
          board_type='greeting',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - none
        # comment_groups - all
        hello.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        hello.enter_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        hello.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        hello.save()

        # 익명 게시판
        anonymous = models.BOARD.objects.create(
          name='익명 게시판',
          board_type='anonymous',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - user, dame, partner, supervisor, sub_supervisor
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        anonymous.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        anonymous.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        anonymous.write_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        anonymous.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        anonymous.save()

        # 문의 게시판
        qna = models.BOARD.objects.create(
          name='문의',
          board_type='qna',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - user, dame, partner, supervisor, sub_supervisor
        # comment_groups - supervisor, sub_supervisor
        qna.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        qna.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        qna.write_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        qna.comment_groups.add(supervisor_group, subsupervisor_group)
        qna.save()

        # 여행지 게시판
        travel_abroad = models.BOARD.objects.create(
          name='여행지',
          board_type='travel',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - partner
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        travel_abroad.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        travel_abroad.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        travel_abroad.write_groups.add(partner_group)
        travel_abroad.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        travel_abroad.save()

        # 쿠폰 거래 게시판
        coupon = models.BOARD.objects.create(
          name='쿠폰 거래',
          board_type='coupon',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - partner, supervisor, sub_supervisor
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        coupon.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        coupon.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        coupon.write_groups.add(partner_group, supervisor_group, subsupervisor_group)
        coupon.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        coupon.save()

        # 후기 게시판
        review = models.BOARD.objects.create(
          name='후기 게시판',
          board_type='review',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - user, dame
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        review.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        review.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        review.write_groups.add(user_group, dame_group)
        review.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        review.save()

        # 공지사항
        notice = models.BOARD.objects.create(
          name='공지사항',
          board_type='board',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - supervisor, sub_supervisor
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        notice.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        notice.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        notice.write_groups.add(supervisor_group, subsupervisor_group)
        notice.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        notice.save()

        # 커뮤니티
        community = models.BOARD.objects.create(
          name='커뮤니티',
          board_type='tree',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - all
        # comment_groups - all
        community.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        community.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        community.write_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        community.comment_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        community.save()

        # 자유 게시판
        free = models.BOARD.objects.create(
          parent_board=community,
          name='자유 게시판',
          board_type='board',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - user, dame
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        free.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        free.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        free.write_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        free.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        free.save()

        # 여성 게시판
        dame = models.BOARD.objects.create(
          parent_board=community,
          name='여성 게시판',
          board_type='board',
        )
        # display_groups - all
        # enter_groups - dame, supervisor, sub_supervisor
        # write_groups - dame
        # comment_groups - dame, supervisor, sub_supervisor
        dame.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        dame.enter_groups.add(dame_group, supervisor_group, subsupervisor_group)
        dame.write_groups.add(dame_group)
        dame.comment_groups.add(dame_group, supervisor_group, subsupervisor_group)
        dame.save()

        # 배너 생성
        top_banner = models.BANNER.objects.create(
          location='top',
          image='/media/default.png',
          link='https://naver.com',
        )
        side_banner = models.BANNER.objects.create(
          location='side',
          image='/media/default.png',
          link='https://naver.com',
        )

        print('데이터베이스 기본 데이터 생성 완료')
    except Exception as e:
      print(str(e))
