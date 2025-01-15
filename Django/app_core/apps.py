from django.apps import AppConfig


class AppCoreConfig(AppConfig):
  default_auto_field = 'django.db.models.BigAutoField'
  name = 'app_core'

  def ready(self):

    try:
      from datetime import datetime
      from app_user import models as user_mo
      from app_partner import models as partner_mo
      from app_supervisor import models as supervisor_mo
      from app_core import models as core_mo
      from app_coupon import models as coupon_mo
      from app_message import models as message_mo
      from app_post import models as post_mo

      if False: # 필요에 따라 데이터베이스 초기화 여부를 결정
        core_mo.CustomUser.objects.all().delete()
        core_mo.SERVER_SETTING.objects.all().delete()
        core_mo.LEVEL_RULE.objects.all().delete()
        coupon_mo.COUPON.objects.all().delete()
        coupon_mo.COUPON_HISTORY.objects.all().delete()
        message_mo.MESSAGE.objects.all().delete()
        partner_mo.CATEGORY.objects.all().delete()
        post_mo.BOARD.objects.all().delete()
        post_mo.POST.objects.all().delete()
        post_mo.AD.objects.all().delete()
        post_mo.COMMENT.objects.all().delete()
        supervisor_mo.BANNER.objects.all().delete()
        user_mo.ACTIVITY.objects.all().delete()

      # 서버 초기 데이터 구성
      # 만약, 초기 데이터가 설정되어있지 않을 경우, 데이터 생성
      is_CustomUser_exist = core_mo.CustomUser.objects.all().count() > 0
      is_SERVER_SETTING_exist = core_mo.SERVER_SETTING.objects.all().count() > 0
      is_LEVEL_RULE_exist = core_mo.LEVEL_RULE.objects.all().count() > 0
      is_CATEGORY_exist = partner_mo.CATEGORY.objects.all().count() > 0
      is_BOARD_exist = post_mo.BOARD.objects.all().count() > 0
      is_ACTIVITY_exist = user_mo.ACTIVITY.objects.all().count() > 0
      is_BANNER_exist = supervisor_mo.BANNER.objects.all().count() > 0
      is_COUPON_exist = coupon_mo.COUPON.objects.all().count() > 0
      is_COUPON_HISTORY_exist = coupon_mo.COUPON_HISTORY.objects.all().count() > 0
      is_MESSAGE_exist = message_mo.MESSAGE.objects.all().count() > 0
      is_POST_exist = post_mo.POST.objects.all().count() > 0
      is_AD_exist = post_mo.AD.objects.all().count() > 0
      is_COMMENT_exist = post_mo.COMMENT.objects.all().count() > 0
      is_all_exist = is_CustomUser_exist and is_SERVER_SETTING_exist and is_LEVEL_RULE_exist and is_CATEGORY_exist and is_BOARD_exist and is_ACTIVITY_exist and is_BANNER_exist and is_COUPON_exist and is_COUPON_HISTORY_exist and is_MESSAGE_exist and is_POST_exist and is_AD_exist and is_COMMENT_exist
      if not is_all_exist: # 초기 데이터가 없을 경우

        # 서버 설정 데이터 생성(server_setting)
        core_mo.SERVER_SETTING.objects.create(
          id='site_name', # 사이트 이름
          value='여행자들의 대화'
        )
        core_mo.SERVER_SETTING.objects.create(
          id='site_logo', # 로고
          value='/media/default.png'
        )
        core_mo.SERVER_SETTING.objects.create(
          id='site_favicon', # 파비콘
          value='/media/default.png'
        )
        core_mo.SERVER_SETTING.objects.create(
          id='company_name', # 회사 이름
          value='company_name'
        )
        core_mo.SERVER_SETTING.objects.create(
          id='company_tel', # 회사 전화번호
          value='company_tel'
        )
        core_mo.SERVER_SETTING.objects.create(
          id='company_email', # 회사 이메일
          value='company_email'
        )
        core_mo.SERVER_SETTING.objects.create(
          id='company_address', # 회사 주소
          value='company_address'
        )
        core_mo.SERVER_SETTING.objects.create(
          id='social_network_x', # X 주소
          value='https://www.x.com'
        )
        core_mo.SERVER_SETTING.objects.create(
          id='social_network_meta', # 메타 주소
          value='https://www.meta.com'
        )
        core_mo.SERVER_SETTING.objects.create(
          id='social_network_instagram', # 인스타그램 주소
          value='https://www.instagram.com'
        )
        core_mo.SERVER_SETTING.objects.create(
          id='register_point', # 가입 시 제공 포인트
          value='1000'
        )
        core_mo.SERVER_SETTING.objects.create(
          id='attend_point', # 출석 시 제공 포인트
          value='100'
        )
        core_mo.SERVER_SETTING.objects.create(
          id='post_point', # 게시물 작성 시 제공 포인트
          value='100'
        )
        core_mo.SERVER_SETTING.objects.create(
          id='review_point', # 리뷰 게시물 작성 시 제공 포인트
          value='100'
        )
        core_mo.SERVER_SETTING.objects.create(
          id='comment_point', # 댓글 작성 시 제공 포인트
          value='50'
        )
        core_mo.SERVER_SETTING.objects.create(
          id='terms', # 이용약관
          value='plz write terms here'
        )

        # 레벨 규칙 데이터 생성(level_rule)
        core_mo.LEVEL_RULE.objects.create(
          level=1, # 레벨
          text_color='#000000', # 레벨 텍스트 색상
          background_color='#cd7f32', # 레벨 배경 색상
          name='1레벨(평민)', # 레벨 이름
          required_point=0 # 레벨업 포인트
        )
        core_mo.LEVEL_RULE.objects.create(
          level=2, # 레벨
          text_color='#000000', # 레벨 텍스트 색상
          background_color='#cd7f32', # 레벨 배경 색상
          name='2레벨(종 9품)', # 레벨 이름
          required_point=100 # 레벨업 포인트
        )
        core_mo.LEVEL_RULE.objects.create(
          level=3, # 레벨
          text_color='#000000', # 레벨 텍스트 색상
          background_color='#cd7f32', # 레벨 배경 색상
          name='3레벨(정 9품)', # 레벨 이름
          required_point=200 # 레벨업 포인트
        )
        core_mo.LEVEL_RULE.objects.create(
          level=4, # 레벨
          text_color='#000000', # 레벨 텍스트 색상
          background_color='#cd7f32', # 레벨 배경 색상
          name='4레벨(종 8품)', # 레벨 이름
          required_point=300 # 레벨업 포인트
        )
        core_mo.LEVEL_RULE.objects.create(
          level=5, # 레벨
          text_color='#000000', # 레벨 텍스트 색상
          background_color='#cd7f32', # 레벨 배경 색상
          name='5레벨(정 8품)', # 레벨 이름
          required_point=400 # 레벨업 포인트
        )
        core_mo.LEVEL_RULE.objects.create(
          level=6, # 레벨
          text_color='#000000', # 레벨 텍스트 색상
          background_color='#cd7f32', # 레벨 배경 색상
          name='6레벨(종 7품)', # 레벨 이름
          required_point=500 # 레벨업 포인트
        )
        core_mo.LEVEL_RULE.objects.create(
          level=7, # 레벨
          text_color='#000000', # 레벨 텍스트 색상
          background_color='#cd7f32', # 레벨 배경 색상
          name='7레벨(정 7품)', # 레벨 이름
          required_point=600 # 레벨업 포인트
        )
        core_mo.LEVEL_RULE.objects.create(
          level=8, # 레벨
          text_color='#000000', # 레벨 텍스트 색상
          background_color='#a9a9a9', # 레벨 배경 색상
          name='8레벨(종 6품)', # 레벨 이름
          required_point=700 # 레벨업 포인트
        )
        core_mo.LEVEL_RULE.objects.create(
          level=9, # 레벨
          text_color='#000000', # 레벨 텍스트 색상
          background_color='#a9a9a9', # 레벨 배경 색상
          name='9레벨(정 6품)', # 레벨 이름
          required_point=800 # 레벨업 포인트
        )
        core_mo.LEVEL_RULE.objects.create(
          level=10, # 레벨
          text_color='#000000', # 레벨 텍스트 색상
          background_color='#a9a9a9', # 레벨 배경 색상
          name='10레벨(종 5품)', # 레벨 이름
          required_point=900 # 레벨업 포인트
        )
        core_mo.LEVEL_RULE.objects.create(
          level=11, # 레벨
          text_color='#000000', # 레벨 텍스트 색상
          background_color='#a9a9a9', # 레벨 배경 색상
          name='11레벨(정 5품)', # 레벨 이름
          required_point=1000 # 레벨업 포인트
        )
        core_mo.LEVEL_RULE.objects.create(
          level=12, # 레벨
          text_color='#000000', # 레벨 텍스트 색상
          background_color='#a9a9a9', # 레벨 배경 색상
          name='12레벨(종 4품)', # 레벨 이름
          required_point=1100 # 레벨업 포인트
        )
        core_mo.LEVEL_RULE.objects.create(
          level=13, # 레벨
          text_color='#000000', # 레벨 텍스트 색상
          background_color='#a9a9a9', # 레벨 배경 색상
          name='13레벨(정 4품)', # 레벨 이름
          required_point=1200 # 레벨업 포인트
        )
        core_mo.LEVEL_RULE.objects.create(
          level=14, # 레벨
          text_color='#000000', # 레벨 텍스트 색상
          background_color='#a9a9a9', # 레벨 배경 색상
          name='14레벨(종 3품)', # 레벨 이름
          required_point=1300 # 레벨업 포인트
        )
        core_mo.LEVEL_RULE.objects.create(
          level=15, # 레벨
          text_color='#000000', # 레벨 텍스트 색상
          background_color='#ffd700', # 레벨 배경 색상
          name='15레벨(정 3품)', # 레벨 이름
          required_point=1400 # 레벨업 포인트
        )
        core_mo.LEVEL_RULE.objects.create(
          level=16, # 레벨
          text_color='#000000', # 레벨 텍스트 색상
          background_color='#ffd700', # 레벨 배경 색상
          name='16레벨(종 2품)', # 레벨 이름
          required_point=1500 # 레벨업 포인트
        )
        core_mo.LEVEL_RULE.objects.create(
          level=17, # 레벨
          text_color='#000000', # 레벨 텍스트 색상
          background_color='#ffd700', # 렠벨 배경 색상
          name='17레벨(정 2품)', # 레벨 이름
          required_point=1600 # 레벨업 포인트
        )
        core_mo.LEVEL_RULE.objects.create(
          level=18, # 레벨
          text_color='#000000', # 레벨 텍스트 색상
          background_color='#ffd700', # 레벨 배경 색상
          name='18레벨(종 1품)', # 레벨 이름
          required_point=1700 # 레벨업 포인트
        )
        core_mo.LEVEL_RULE.objects.create(
          level=19, # 레벨
          text_color='#000000', # 레벨 텍스트 색상
          background_color='#ffd700', # 레벨 배경 색상
          name='19레벨(정 1품)', # 레벨 이름
          required_point=1800 # 레벨업 포인트
        )
        core_mo.LEVEL_RULE.objects.create(
          level=20, # 레벨
          text_color='#000000', # 레벨 텍스트 색상
          background_color='#ffd700', # 레벨 배경 색상
          name='20레벨(세자)', # 레벨 이름
          required_point=1900 # 레벨업 포인트
        )
        core_mo.LEVEL_RULE.objects.create(
          level=21, # 레벨
          text_color='#000000', # 레벨 텍스트 색상
          background_color='#ffd700', # 레벨 배경 색상
          name='21레벨(왕)', # 레벨 이름
          required_point=2000 # 레벨업 포인트
        )

        # 파트너 카테고리 데이터 생성(partner_category)
        partner_mo.CATEGORY.objects.create(
          parent_id='', # 최상위 카테고리
          name='서비스' # 카테고리 이름(최대 100자)
        )
        service_category = partner_mo.CATEGORY.objects.get(name='서비스')
        partner_mo.CATEGORY.objects.create(
          parent_id=service_category.id, # 서비스 카테고리
          name='투어' # 카테고리 이름(최대 100자)
        )
        tour_category = partner_mo.CATEGORY.objects.get(name='투어')
        partner_mo.CATEGORY.objects.create(
          parent_id='', # 최상위 카테고리
          name='음식' # 카테고리 이름(최대 100자)
        )
        food_category = partner_mo.CATEGORY.objects.get(name='음식')
        partner_mo.CATEGORY.objects.create(
          parent_id=food_category.id, # 음식 카테고리
          name='카페' # 카테고리 이름(최대 100자)
        )
        cafe_category = partner_mo.CATEGORY.objects.get(name='카페')
        partner_mo.CATEGORY.objects.create(
          parent_id=food_category.id, # 음식 카테고리
          name='레스토랑' # 카테고리 이름(최대 100자)
        )
        restaurant_category = partner_mo.CATEGORY.objects.get(name='레스토랑')
        partner_mo.CATEGORY.objects.create(
          parent_id=restaurant_category.id, # 레스토랑 카테고리
          name='한식' # 카테고리 이름(최대 100자)
        )
        korean_category = partner_mo.CATEGORY.objects.get(name='한식')
        partner_mo.CATEGORY.objects.create(
          parent_id=restaurant_category.id, # 레스토랑 카테고리
          name='중식' # 카테고리 이름(최대 100자)
        )
        chinese_category = partner_mo.CATEGORY.objects.get(name='중식')

        # 사용자 데이터 생성(admin, supervisor, sub_supervisor, user, partner, dame)
        # 사용자 데이터 생성(admin)
        core_mo.CustomUser.objects.create_superuser(
          username='admin', # ad login id
          password='admin1!',
          first_name='ADMIN', # as nickname
          last_name='',
          email='admin@travelertalk.com',
          account_type='admin',
          status='active',
        )
        admin = core_mo.CustomUser.objects.get(username='admin')

        # 사용자 데이터 생성(supervisor)
        core_mo.CustomUser.objects.create_user(
          username='supervisor', # sp login id
          password='supervisor1!',
          first_name='관리자', # as nickname
          last_name='',
          email='',
          account_type='supervisor',
          status='active',
          supervisor_permissions='user, partner, supervisor, post, coupon, message, setting'
        )
        supervisor = core_mo.CustomUser.objects.get(username='supervisor')

        # 사용자 데이터 생성(sub_supervisor)
        core_mo.CustomUser.objects.create_user(
          username='sub_supervisor', # ssp login id
          password='sub_supervisor1!',
          first_name='부관리자', # as nickname
          last_name='',
          email='',
          account_type='sub_supervisor',
          status='active',
          supervisor_permissions='user, partner, supervisor, post, coupon, message'
        )
        sub_supervisor = core_mo.CustomUser.objects.get(username='sub_supervisor')

        # 사용자 데이터 생성(user)
        core_mo.CustomUser.objects.create_user(
          username='user', # us login id
          password='user1!',
          first_name='여행자1', # as nickname
          last_name='',
          email='',
          account_type='user',
          status='active',
          note='테스트용 사용자 데이터입니다. 아이디: user, 비밀번호: user1!',
          user_usable_point=1000,
          user_level_point=1500,
          user_level=2,
        )
        user = core_mo.CustomUser.objects.get(username='user')

        # 파트너 데이터 생성(partner)
        core_mo.CustomUser.objects.create_user(
          username='partner', # pt login id
          password='partner1!',
          first_name='파트너1', # as nickname
          last_name='',
          email='',
          account_type='partner',
          status='active',
          note='테스트용 파트너 데이터입니다. 아이디: partner, 비밀번호: partner1!',
          partner_tel='01012345678',
          partner_address='서울시 강남구 역삼동 123-456',
          partner_categories='음식 > 레스토랑 > 한식',
        )
        partner = core_mo.CustomUser.objects.get(username='partner')

        # 사용자 데이터 생성(dame)
        core_mo.CustomUser.objects.create_user(
          username='dame', # dm login id
          password='dame1!',
          first_name='Dame2', # as nickname
          last_name='',
          email='',
          account_type='dame',
          status='active',
          note='테스트용 사용자 데이터입니다. 아이디: dame, 비밀번호: dame1!',
          user_usable_point=1200,
          user_level_point=1700,
          user_level=3,
        )
        dame = core_mo.CustomUser.objects.get(username='dame')

        # 게시판 데이터 생성(board)
        post_mo.BOARD.objects.create(
          parent_id='', # 상위 게시판 ID(없으면 공백)
          name='공지사항', # 게시판 이름(최대 100자)
          post_type='notice', # 게시물 타입(card, box, list, event, none-게시물 작성 불가, 리다이렉트 안됨)
          display_permissions='guest, user, dame, partner, supervisor, sub_supervisor', # 게시판 표시 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
          enter_permissions='guest, user, dame, partner, supervisor, sub_supervisor', # 게시판 접근 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
          write_permissions='supervisor, sub_supervisor', # 게시판 작성 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
          comment_permissions='supervisor, sub_supervisor' # 게시판 댓글 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
        )
        notice_board = post_mo.BOARD.objects.get(name='공지사항')
        post_mo.BOARD.objects.create(
          parent_id='', # 상위 게시판 ID(없으면 공백)
          name='이벤트', # 게시판 이름(최대 100자)
          post_type='event', # 게시물 타입(card, box, list, event, none-게시물 작성 불가, 리다이렉트 안됨)
          display_permissions='guest, user, dame, partner, supervisor, sub_supervisor', # 게시판 표시 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
          enter_permissions='guest, user, dame, partner, supervisor, sub_supervisor', # 게시판 접근 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
          write_permissions='supervisor, sub_supervisor', # 게시판 작성 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
          comment_permissions='user, dame, partner, supervisor, sub_supervisor' # 게시판 댓글 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
        )
        event_board = post_mo.BOARD.objects.get(name='이벤트')
        post_mo.BOARD.objects.create(
          parent_id='', # 상위 게시판 ID(없으면 공백)
          name='출석 게시판', # 게시판 이름(최대 100자)
          post_type='attendance', # 게시물 타입(card, box, list, event, none-게시물 작성 불가, 리다이렉트 안됨)
          display_permissions='user, dame, partner, supervisor, sub_supervisor', # 게시판 표시 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
          enter_permissions='user, dame, partner, supervisor, sub_supervisor', # 게시판 접근 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
          write_permissions='',
          comment_permissions='user, dame, partner, supervisor, sub_supervisor' # 게시판 댓글 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
        )
        attend_board = post_mo.BOARD.objects.get(name='출석 게시판')
        post_mo.BOARD.objects.create(
          parent_id='', # 상위 게시판 ID(없으면 공백)
          name='가입인사 게시판', # 게시판 이름(최대 100자)
          post_type='greeting', # 게시물 타입(card, box, list, event, none-게시물 작성 불가, 리다이렉트 안됨)
          display_permissions='user, dame, partner, supervisor, sub_supervisor', # 게시판 표시 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
          enter_permissions='user, dame, partner, supervisor, sub_supervisor', # 게시판 접근 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
          write_permissions='',
          comment_permissions='user, dame, partner, supervisor, sub_supervisor' # 게시판 댓글 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
        )
        greet_board = post_mo.BOARD.objects.get(name='가입인사 게시판')
        post_mo.BOARD.objects.create(
          parent_id='', # 상위 게시판 ID(없으면 공백)
          name='여행지', # 게시판 이름(최대 100자)
          post_type='none', # 게시물 타입(card, box, list, event, none-게시물 작성 불가, 리다이렉트 안됨)
          display_permissions='guest, user, dame, partner, supervisor, sub_supervisor', # 게시판 표시 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
          enter_permissions='guest, user, dame, partner, supervisor, sub_supervisor', # 게시판 접근 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
          write_permissions='',
          comment_permissions=''
        )
        tour_board = post_mo.BOARD.objects.get(name='여행지')
        post_mo.BOARD.objects.create(
          parent_id=tour_board.id, # 상위 게시판 ID(없으면 공백)
          name='국내', # 게시판 이름(최대 100자)
          post_type='travel', # 게시물 타입(card, box, list, event, none-게시물 작성 불가, 리다이렉트 안됨)
          display_permissions='guest, user, dame, partner, supervisor, sub_supervisor', # 게시판 표시 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
          enter_permissions='guest, user, dame, partner, supervisor, sub_supervisor', # 게시판 접근 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
          write_permissions='partner',
          comment_permissions='user, dame, partner, supervisor, sub_supervisor' # 게시판 댓글 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
        )
        domestic_board = post_mo.BOARD.objects.get(name='국내')
        post_mo.BOARD.objects.create(
          parent_id=tour_board.id, # 상위 게시판 ID(없으면 공백)
          name='해외', # 게시판 이름(최대 100자)
          post_type='none', # 게시물 타입(card, box, list, event, none-게시물 작성 불가, 리다이렉트 안됨)
          display_permissions='guest, user, dame, partner, supervisor, sub_supervisor', # 게시판 표시 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
          enter_permissions='guest, user, dame, partner, supervisor, sub_supervisor', # 게시판 접근 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
          write_permissions='',
          comment_permissions='',
        )
        abroad_board = post_mo.BOARD.objects.get(name='해외')
        post_mo.BOARD.objects.create(
          parent_id=abroad_board.id, # 상위 게시판 ID(없으면 공백)
          name='유럽', # 게시판 이름(최대 100자)
          post_type='none', # 게시물 타입(card, box, list, event, none-게시물 작성 불가, 리다이렉트 안됨)
          display_permissions='guest, user, dame, partner, supervisor, sub_supervisor', # 게시판 표시 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
          enter_permissions='guest, user, dame, partner, supervisor, sub_supervisor', # 게시판 접근 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
          write_permissions='',
          comment_permissions='' # 게시판 댓글 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
        )
        europe_board = post_mo.BOARD.objects.get(name='유럽')
        post_mo.BOARD.objects.create(
          parent_id=europe_board.id, # 상위 게시판 ID(없으면 공백)
          name='프랑스', # 게시판 이름(최대 100자)
          post_type='travel', # 게시물 타입(card, box, list, event, none-게시물 작성 불가, 리다이렉트 안됨)
          display_permissions='guest, user, dame, partner, supervisor, sub_supervisor', # 게시판 표시 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
          enter_permissions='guest, user, dame, partner, supervisor, sub_supervisor', # 게시판 접근 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
          write_permissions='partner',
          comment_permissions='user, dame, partner, supervisor, sub_supervisor' # 게시판 댓글 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
        )
        france_board = post_mo.BOARD.objects.get(name='프랑스')
        post_mo.BOARD.objects.create(
          parent_id='', # 상위 게시판 ID(없으면 공백)
          name='커뮤니티', # 게시판 이름(최대 100자)
          post_type='none', # 게시물 타입(card, box, list, event, none-게시물 작성 불가, 리다이렉트 안됨)
          display_permissions='guest, user, dame, partner, supervisor, sub_supervisor', # 게시판 표시 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
          enter_permissions='guest, user, dame, partner, supervisor, sub_supervisor', # 게시판 접근 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
          write_permissions='',
          comment_permissions=''
        )
        community_board = post_mo.BOARD.objects.get(name='커뮤니티')
        post_mo.BOARD.objects.create(
          parent_id=community_board.id, # 상위 게시판 ID(없으면 공백)
          name='리뷰 게시판', # 게시판 이름(최대 100자)
          post_type='review', # 게시물 타입(card, box, list, event, none-게시물 작성 불가, 리다이렉트 안됨)
          display_permissions='user, dame, partner, supervisor, sub_supervisor', # 게시판 표시 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
          enter_permissions='user, dame, partner, supervisor, sub_supervisor', # 게시판 접근 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
          write_permissions='user, dame',
          comment_permissions='user, dame, partner, supervisor, sub_supervisor' # 게시판 댓글 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
        )
        review_board = post_mo.BOARD.objects.get(name='리뷰 게시판')
        post_mo.BOARD.objects.create(
          parent_id=community_board.id, # 상위 게시판 ID(없으면 공백)
          name='자유 게시판', # 게시판 이름(최대 100자)
          post_type='list', # 게시물 타입(card, box, list, event, none-게시물 작성 불가, 리다이렉트 안됨)
          display_permissions='guest, user, dame, partner, supervisor, sub_supervisor', # 게시판 표시 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
          enter_permissions='guest, user, dame, partner, supervisor, sub_supervisor', # 게시판 접근 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
          write_permissions='user, dame',
          comment_permissions='user, dame, partner, supervisor, sub_supervisor' # 게시판 댓글 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
        )
        free_board = post_mo.BOARD.objects.get(name='자유 게시판')
        post_mo.BOARD.objects.create(
          parent_id=community_board.id, # 상위 게시판 ID(없으면 공백)
          name='dame 게시판', # 게시판 이름(최대 100자)
          post_type='list', # 게시물 타입(card, box, list, event, none-게시물 작성 불가, 리다이렉트 안됨)
          display_permissions='user, dame, partner, supervisor, sub_supervisor', # 게시판 표시 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
          enter_permissions='dame, partner, supervisor, sub_supervisor', # 게시판 접근 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
          write_permissions='dame',
          comment_permissions='dame, supervisor, sub_supervisor' # 게시판 댓글 권한(user, dame, partner, supervisor, sub_supervisor. ,로 구분)
        )
        dame_board = post_mo.BOARD.objects.get(name='dame 게시판')

        # 게시글 데이터 생성(post)
        # 자유게시판에 게시글 101개 생성
        for i in range(1, 101):
          post_mo.POST.objects.create(
            board_id=f'{community_board.id},{free_board.id}',
            author_id=user.username, # 작성자 ID
            title='자유게시판 게시글 ' + str(i), # 제목
            content='자유게시판 게시글 ' + str(i) + ' 내용입니다.', # 내용
          )
          post = post_mo.POST.objects.get(title='자유게시판 게시글 ' + str(i))
          for i in range(1, 6):
            post_mo.COMMENT.objects.create(
              post_id=post.id, # 게시글 ID
              author_id=user.username, # 작성자 ID
              content='자유게시판 게시글 ' + str(i) + ' 댓글 ' + str(i) + ' 내용입니다.' # 내용
            )

        # 여행지 > 해외 > 유럽에 게시글 생성
        post_mo.POST.objects.create(
          board_id=f'{tour_board.id},{abroad_board.id},{europe_board.id},{france_board.id}',
          author_id=partner.username, # 작성자 ID
          title='프랑스 여행지 게시글', # 제목
          content='프랑스 여행지 게시글 내용입니다.', # 내용
          images='/media/default.png, /media/default.png, /media/default.png',
        )
        travel_post = post_mo.POST.objects.get(title='프랑스 여행지 게시글')
        post_mo.AD.objects.create(
          post_id=travel_post.id, # 게시글 ID
          start_dt=datetime.strptime('2021-01-01', '%Y-%m-%d'), # 광고 시작일
          end_dt=datetime.strptime('2025-12-31', '%Y-%m-%d'), # 광고 종료일
          status='active', # 광고 상태
          weight=1, # 광고 가중치
        )
        ad = post_mo.AD.objects.get(post_id=travel_post.id)
        travel_post.ad_id = ad.id
        travel_post.save()

        # 쿠폰 데이터 생성(coupon)
        # 파트너 계정에 쿠폰 11개 생성
        for i in range(1, 11):
          coupon_mo.COUPON.objects.create(
            code='partner_coupon_' + str(i), # 쿠폰 코드
            create_account_id=partner.username, # 발급 계정 ID
            own_user_id=user.username, # 소유 계정 ID
            name='파트너 쿠폰 ' + str(i), # 쿠폰 이름
            description='파트너 쿠폰 ' + str(i) + ' 설명입니다.', # 쿠폰 설명
            images='/media/default.png, /media/default.png, /media/default.png',
            post_id=travel_post.id, # 게시글 ID
            required_point=1000, # 필요 포인트
          )

        # 배너 데이터 생성(banner)
        # 메인 배너 3개 생성
        for i in range(1, 4):
          supervisor_mo.BANNER.objects.create(
            location='top', # 배너 위치
            display_order=i, # 배너 표시 순서
            image='/media/default.png', # 배너 이미지
            link='https://naver.com', # 배너 링크
          )
        for i in range(1, 4):
          supervisor_mo.BANNER.objects.create(
            location='side', # 배너 위치
            display_order=i, # 배너 표시 순서
            image='/media/default.png', # 배너 이미지
            link='https://naver.com', # 배너 링크
          )
        print('데이터베이스 기본 데이터 생성 완료')
    except Exception as e:
      print(str(e))
