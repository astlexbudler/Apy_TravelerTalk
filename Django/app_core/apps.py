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
          is_staff=True,
          is_superuser=True,
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
        # 골프, 숙박, 스파, 맛집, 유직지, 술집, 마사지, 헤어살롱, 축제, 피부샵
        # 기타(노래발, 풀빌라, 카지노, 그 외)
        golf = models.CATEGORY.objects.create(
          name='골프',
        )

        accommodation = models.CATEGORY.objects.create(
          name='숙박',
        )

        spa = models.CATEGORY.objects.create(
          name='스파',
        )

        restaurant = models.CATEGORY.objects.create(
          name='맛집',
        )

        travel_guide = models.CATEGORY.objects.create(
          name='유직지',
        )

        bar = models.CATEGORY.objects.create(
          name='술집',
        )

        massage = models.CATEGORY.objects.create(
          name='마사지',
        )

        hair_salon = models.CATEGORY.objects.create(
          name='헤어살롱',
        )

        festival = models.CATEGORY.objects.create(
          name='축제',
        )

        skin_shop = models.CATEGORY.objects.create(
          name='피부샵',
        )

        etc = models.CATEGORY.objects.create(
          name='기타',
        )

        karaoke = models.CATEGORY.objects.create(
          parent_category=etc,
          name='노래방',
        )

        pool_villa = models.CATEGORY.objects.create(
          parent_category=etc,
          name='풀빌라',
        )

        casino = models.CATEGORY.objects.create(
          parent_category=etc,
          name='카지노',
        )

        other = models.CATEGORY.objects.create(
          parent_category=etc,
          name='그 외',
        )

        # BOARD: 게시판 테이블 사전 설정
        # 강남, 서울, 인천/부천, 경기, 대전/충청, 대구/구미, 경상, 광주/전라, 강원/제주
        # 해외(필리핀, 태국, 캄보디아, 일본, 베트남)
        # 커뮤니티(자유게시판, 출석체크, 가입인사, 익명게시판, 미녀들의수다, 정보공유/교환, 구인/구직, 쿠폰 거래, 브론즈 게시판, 실버 게시판, 골드 게시판)
        # 이벤트 게시판
        # 후기 게시판
        # 제휴업체 게시판
        # 문의 게시판

        gangnam = models.BOARD.objects.create(
          name='강남',
          board_type='travel',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - partner
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        gangnam.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        gangnam.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        gangnam.write_groups.add(partner_group)
        gangnam.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        gangnam.save()

        seoul = models.BOARD.objects.create(
          name='서울',
          board_type='travel',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - partner
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        seoul.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        seoul.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        seoul.write_groups.add(partner_group)
        seoul.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        seoul.save()

        incheon = models.BOARD.objects.create(
          name='인천/부천',
          board_type='travel',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - partner
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        incheon.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        incheon.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        incheon.write_groups.add(partner_group)
        incheon.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        incheon.save()

        gyeonggi = models.BOARD.objects.create(
          name='경기',
          board_type='travel',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - partner
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        gyeonggi.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        gyeonggi.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        gyeonggi.write_groups.add(partner_group)
        gyeonggi.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        gyeonggi.save()

        daejeon = models.BOARD.objects.create(
          name='대전/충청',
          board_type='travel',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - partner
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        daejeon.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        daejeon.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        daejeon.write_groups.add(partner_group)
        daejeon.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        daejeon.save()

        daegu = models.BOARD.objects.create(
          name='대구/구미',
          board_type='travel',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - partner
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        daegu.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        daegu.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        daegu.write_groups.add(partner_group)
        daegu.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        daegu.save()

        gyeongsang = models.BOARD.objects.create(
          name='경상',
          board_type='travel',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - partner
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        gyeongsang.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        gyeongsang.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        gyeongsang.write_groups.add(partner_group)
        gyeongsang.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        gyeongsang.save()

        gwangju = models.BOARD.objects.create(
          name='광주/전라',
          board_type='travel',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - partner
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        gwangju.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        gwangju.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        gwangju.write_groups.add(partner_group)
        gwangju.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        gwangju.save()

        gangwon = models.BOARD.objects.create(
          name='강원/제주',
          board_type='travel',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - partner
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        gangwon.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        gangwon.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        gangwon.write_groups.add(partner_group)
        gangwon.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        gangwon.save()

        abroad = models.BOARD.objects.create(
          name='해외',
          board_type='travel',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - partner
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        abroad.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        abroad.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        abroad.write_groups.add(partner_group)
        abroad.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        abroad.save()

        # 필리핀
        philippines = models.BOARD.objects.create(
          parent_board=abroad,
          name='필리핀',
          board_type='travel',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - partner
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        philippines.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        philippines.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        philippines.write_groups.add(partner_group)
        philippines.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        philippines.save()

        # 태국
        thailand = models.BOARD.objects.create(
          parent_board=abroad,
          name='태국',
          board_type='travel',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - partner
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        thailand.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        thailand.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        thailand.write_groups.add(partner_group)
        thailand.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        thailand.save()

        # 캄보디아
        cambodia = models.BOARD.objects.create(
          parent_board=abroad,
          name='캄보디아',
          board_type='travel',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - partner
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        cambodia.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        cambodia.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        cambodia.write_groups.add(partner_group)
        cambodia.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        cambodia.save()

        # 일본
        japan = models.BOARD.objects.create(
          parent_board=abroad,
          name='일본',
          board_type='travel',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - partner
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        japan.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        japan.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        japan.write_groups.add(partner_group)
        japan.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        japan.save()

        # 베트남
        vietnam = models.BOARD.objects.create(
          parent_board=abroad,
          name='베트남',
          board_type='travel',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - partner
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        vietnam.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        vietnam.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        vietnam.write_groups.add(partner_group)
        vietnam.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        vietnam.save()

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
        # write_groups - user, dame, partner, supervisor, sub_supervisor
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        free.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        free.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        free.write_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        free.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        free.save()

        # 출석체크 게시판
        attend = models.BOARD.objects.create(
          parent_board=community,
          name='출석체크',
          board_type='attendance',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - none
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        attend.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        attend.enter_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        attend.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        attend.save()

        # 가입인사 게시판
        hello = models.BOARD.objects.create(
          parent_board=community,
          name='가입인사',
          board_type='greeting',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - none
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        hello.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        hello.enter_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        hello.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        hello.save()

        # 익명 게시판
        anonymous = models.BOARD.objects.create(
          parent_board=community,
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

        # 미녀들의 수다
        beauty = models.BOARD.objects.create(
          parent_board=community,
          name='미녀들의 수다',
          board_type='board',
        )
        # display_groups - all
        # enter_groups - dame, supervisor, sub_supervisor
        # write_groups - dame, supervisor, sub_supervisor
        # comment_groups - dame, supervisor, sub_supervisor
        beauty.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        beauty.enter_groups.add(dame_group, supervisor_group, subsupervisor_group)
        beauty.write_groups.add(dame_group, supervisor_group, subsupervisor_group)
        beauty.comment_groups.add(dame_group, supervisor_group, subsupervisor_group)
        beauty.save()

        # 정보공유/교환
        information = models.BOARD.objects.create(
          parent_board=community,
          name='정보공유/교환',
          board_type='board',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - user, dame, partner, supervisor, sub_supervisor
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        information.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        information.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        information.write_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        information.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        information.save()

        # 구인/구직
        recruitment = models.BOARD.objects.create(
          parent_board=community,
          name='구인/구직',
          board_type='board',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - user, dame, partner, supervisor, sub_supervisor
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        recruitment.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        recruitment.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        recruitment.write_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        recruitment.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        recruitment.save()

        # 쿠폰 거래 게시판
        coupon = models.BOARD.objects.create(
          parent_board=community,
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

        # 브론즈 게시판
        bronze = models.BOARD.objects.create(
          parent_board=community,
          name='브론즈 게시판',
          board_type='board',
          level_cut=1,
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - user, dame, supervisor, sub_supervisor
        # comment_groups - user, dame, supervisor, sub_supervisor
        bronze.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        bronze.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        bronze.write_groups.add(user_group, dame_group, supervisor_group, subsupervisor_group)
        bronze.comment_groups.add(user_group, dame_group, supervisor_group, subsupervisor_group)
        bronze.save()

        # 실버 게시판
        silver = models.BOARD.objects.create(
          parent_board=community,
          name='실버 게시판',
          board_type='board',
          level_cut=2,
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - user, dame, supervisor, sub_supervisor
        # comment_groups - user, dame, supervisor, sub_supervisor
        silver.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        silver.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        silver.write_groups.add(user_group, dame_group, supervisor_group, subsupervisor_group)
        silver.comment_groups.add(user_group, dame_group, supervisor_group, subsupervisor_group)
        silver.save()

        # 골드 게시판
        gold = models.BOARD.objects.create(
          parent_board=community,
          name='골드 게시판',
          board_type='board',
          level_cut=3,
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - user, dame, supervisor, sub_supervisor
        # comment_groups - user, dame, supervisor, sub_supervisor
        gold.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        gold.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        gold.write_groups.add(user_group, dame_group, supervisor_group, subsupervisor_group)
        gold.comment_groups.add(user_group, dame_group, supervisor_group, subsupervisor_group)
        gold.save()

        # 이벤트 게시판
        event = models.BOARD.objects.create(
          name='이벤트',
          board_type='board',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - supervisor, sub_supervisor
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        event.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        event.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        event.write_groups.add(supervisor_group, subsupervisor_group)
        event.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        event.save()

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

        # 제휴업체 게시판
        partner = models.BOARD.objects.create(
          name='제휴업체',
          board_type='board',
        )
        # display_groups - all
        # enter_groups - all
        # write_groups - partner, supervisor, sub_supervisor
        # comment_groups - user, dame, partner, supervisor, sub_supervisor
        partner.display_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        partner.enter_groups.add(guest_group, user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        partner.write_groups.add(partner_group, supervisor_group, subsupervisor_group)
        partner.comment_groups.add(user_group, dame_group, partner_group, supervisor_group, subsupervisor_group)
        partner.save()

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