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
      from datetime import datetime
      from django.contrib.auth.models import Group
      from . import models

      # 서버 초기 데이터 구성
      # 만약, 초기 데이터가 설정되어있지 않을 경우, 데이터 생성
      is_SERVER_SETTING_exist = models.SERVER_SETTING.objects.all().count() > 0
      if not is_SERVER_SETTING_exist: # 초기 데이터가 없을 경우

        # SERVER_SETTING: 서버 설정 테이블
        models.SERVER_SETTING.objects.create(
          name='site_logo', # 로고
          value='/media/logo.png'
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
          name='review_point', # 리뷰 게시물 작성 시 제공 포인트
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
          required_point=0 # 레벨업 포인트
        )
        models.LEVEL_RULE.objects.create(
          level=2, # 레벨
          text='2레벨', # 레벨 이름
          text_color='#000000', # 레벨 텍스트 색상
          background_color='#cd7f32', # 레벨 배경 색상
          required_point=100 # 레벨업 포인트
        )
        models.LEVEL_RULE.objects.create(
          level=3, # 레벨
          text='3레벨', # 레벨 이름
          text_color='#000000', # 레벨 텍스트 색상
          background_color='#cd7f32', # 레벨 배경 색상
          required_point=200 # 레벨업 포인트
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
        sub_supervisor_group = Group.objects.create(
          name='sub_supervisor' # 부관리자 그룹
        )
        supervisor_group = Group.objects.create(
          name='supervisor' # 관리자 그룹
        )

        # ACCOUNT: 계정 테이블
        user = models.ACCOUNT.objects.create(
          username='user', # 사용자 아이디
          password='user1!', # 비밀번호
          first_name='닉네임1', # 사용자 이름
          last_name='',
          email='',
          status = 'active', # 계정 상태
          note='테스트용 사용자 데이터입니다. 아이디: user, 비밀번호: user1!',
          coupon_point=1000, # 쿠폰 포인트
          level_point=100, # 레벨 포인트
          tel='', # 연락처
          address='', # 주소
          subsupervisor_permissions='', # 부관리자 권한
        )
        user.groups.add(user_group)
        user.save()

        dame = models.ACCOUNT.objects.create(
          username='dame', # Dame 아이디
          password='dame1!', # 비밀번호
          first_name='닉네임2', # 낙네임
          last_name='',
          email='',
          status = 'pending', # 계정 상태
          note='테스트용 사용자 데이터입니다. 아이디: dame, 비밀번호: dame1!',
          coupon_point=100, # 쿠폰 포인트
          level_point=200, # 레벨 포인트
          tel='', # 연락처
          address='', # 주소
          subsupervisor_permissions='', # 부관리자 권한
        )
        dame.groups.add(user_group)
        dame.save()

        partner = models.ACCOUNT.objects.create(
          username='partner', # 파트너 아이디
          password='partner1!', # 비밀번호
          first_name='닉네임4', # 닉네임
          last_name='업체명1', # 파트너 업체명
          email='applify.kr@gmail.com', # 파트너 이메일
          status = 'pending', # 계정 상태
          note='테스트용 파트너 데이터입니다. 아이디: partner, 비밀번호: partner1!',
          coupon_point=0,
          level_point=0,
          tel='01041098317', # 연락처
          address='대전광역시 서구 만년동', # 주소
          subsupervisor_permissions='', # 부관리자 권한
        )

        subsupervisor = models.ACCOUNT.objects.create(
          username='subsupervisor', # 부관리자 아이디
          password='subsupervisor!', # 비밀번호
          first_name='닉네임6', # 닉네임
          last_name='',
          email='',
          status = 'active', # 계정 상태
          note='테스트용 부관리자 데이터입니다. 아이디: subsupervisor, 비밀번호: subsupervisor!',
          coupon_point=0,
          level_point=0,
          tel='', # 연락처
          address='', # 주소
          subsupervisor_permissions='post, coupon, message, banner, setting', # 부관리자 권한
        )
        subsupervisor.groups.add(user_group)
        subsupervisor.groups.add(dame_group)
        subsupervisor.groups.add(sub_supervisor_group)
        subsupervisor.save()

        supervisor = models.ACCOUNT.objects.create(
          username='supervisor', # 관리자 아이디
          password='supervisor1!', # 비밀번호
          first_name='닉네임7', # 닉네임
          last_name='',
          email='',
          status = 'active', # 계정 상태
          note='테스트용 관리자 데이터입니다. 아이디: supervisor, 비밀번호: supervisor1!',
          coupon_point=0,
          level_point=0,
          tel='', # 연락처
          address='', # 주소
          subsupervisor_permissions='',
        )
        supervisor.groups.add(user_group)
        supervisor.groups.add(dame_group)
        supervisor.groups.add(sub_supervisor_group)
        supervisor.groups.add(supervisor_group)
        supervisor.save()

        # CATEGORY: 카테고리 테이블
        abroad = models.CATEGORY.objects.create(
          name='해외'
        )
        service = models.CATEGORY.objects.create(
          parent_id=abroad.id,
          name='서비스'
        )
        tour = models.CATEGORY.objects.create(
          parent_id=service.id,
          name='투어'
        )

        # BOARD: 게시판 테이블
        travel_abroad = models.BOARD.objects.create(
          name='해외 여행지',
          board_type='travel',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - partner
        # comment_groups - user, dame
        travel_abroad.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, sub_supervisor_group)
        travel_abroad.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, sub_supervisor_group)
        travel_abroad.write_groups.add(partner_group)
        travel_abroad.comment_groups.add(user_group, dame_group)
        travel_abroad.save()

        event = models.BOARD.objects.create(
          name='이벤트',
          board_type='event',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - supervisor, sub_supervisor
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        event.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, sub_supervisor_group)
        event.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, sub_supervisor_group)
        event.write_groups.add(supervisor_group, sub_supervisor_group)
        event.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, sub_supervisor_group)
        event.save()

        community = models.BOARD.objects.create(
          name='커뮤니티',
          board_type='tree',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - none
        # comment_groups - none
        community.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, sub_supervisor_group)
        community.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, sub_supervisor_group)
        community.save()

        free = models.BOARD.objects.create(
          parent_id=community.id,
          name='자유 게시판',
          board_type='board',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - user, dame
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        free.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, sub_supervisor_group)
        free.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, sub_supervisor_group)
        free.write_groups.add(user_group, dame_group)
        free.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, sub_supervisor_group)
        free.save()

        dame = models.BOARD.objects.create(
          parent_id=community.id,
          name='여성 게시판',
          board_type='board',
        )
        # display_groups - all
        # enter_groups - dame, supervisor, sub_supervisor
        # write_groups - dame
        # comment_groups - dame, supervisor, sub_supervisor
        dame.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, sub_supervisor_group)
        dame.enter_groups.add(dame_group, supervisor_group, sub_supervisor_group)
        dame.write_groups.add(dame_group)
        dame.comment_groups.add(dame_group, supervisor_group, sub_supervisor_group)
        dame.save()

        review = models.BOARD.objects.create(
          parent_id=community.id,
          name='리뷰 게시판',
          board_type='review',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - user, dame
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        review.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, sub_supervisor_group)
        review.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, sub_supervisor_group)
        review.write_groups.add(user_group, dame_group)
        review.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, sub_supervisor_group)
        review.save()

        # 자유 개시판에 글 101개 생성
        for i in range(1, 101):
          post = models.POST.objects.create(
            author=user,
            title='자유 게시판 게시글 ' + str(i),
            content='자유 게시판 게시글 ' + str(i) + ' 내용입니다.',
          )
          post.boards.add(community, free)
          post.save()
          # 게시글에 댓글 5개 생성
          for j in range(1, 6):
            comment = models.COMMENT.objects.create(
              post=post,
              author=user,
              content='자유 게시판 게시글 ' + str(i) + ' 댓글 ' + str(j) + ' 내용입니다.'
            )

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
