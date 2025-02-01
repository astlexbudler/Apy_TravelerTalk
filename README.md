# 여행자들의 대화(진행중)

Django를 이용하여 제작한 여행자들 대화 익명 여행지 커뮤니티 사이트.  
각 기능별로 별도의 app으로 구분하여 제작. 실험적으로 모든 테이블을 app_core에 작성하여 관리.

---

## 개요

일반 사용자(user), 여성 회원(dame), 파트너 회원(partner), 상위 관리자(supervisor), 하위 관리자(sub_supervisor), 데이터베이스 관리자(admin)로 구분된 회원 종류와 레벨 포인트외 레벨, 쿠폰 포인트와 쿠폰, 광고 배너 및 광고 게시글, 별도의 리뷰 게시판과 출석체크, 가입 인사 게시판, 회원간 쪽지 기능을 가지는 여행지 정보 공유 커뮤니티 사이트. 파트너 계정은 여행지 게시판에 여행지 게시글을 1개씩 작성 가능하며, 여행지 게시글는 광고를 적용할 수 있습니다. 일반 사용자 및 여성 회원은 리뷰 게시글을 작성 가능하며 리뷰 게시글은 리뷰 게시판에서 일간, 주간, 월간 베스트 게시글로 추천됩니다.

### 프로젝트 실행 방법

1. Django/{project_name} 디렉토리로 이동합니다.
2. 가상환경을 생성하고 실행합니다.
3. OS에 따라서 Win 기반 OS의 경우 init.ps1(PowerShell)을 실행합니다. Linux 기반 OS의 경우 init.sh를 실행합니다. requirements와 migration 및 초기 필요한 데이터가 자동으로 구성됩니다.
4. python manage.py runserver 또는 python3 manage.py runserver 명령어를 이용하여 Django 프로젝트를 실행할 수 있습니다.
5. 데이터베이스 초기화 시 다시 init 파일을 실행하여 초기 상태로 되돌릴 수 있습니다. 작성된 코드는 복구되지 않습니다.
6. .env등의 환경 변수 설정이 필요한 경우(또는 credentials.json 등등), Django 프로젝트의 루트 디렉토리에 환경 변수 파일을 저장합니다.

---

## 주의

⚠️ 시크릿 인증 키를 직접 하드코딩하지 마세요. credentials.json 파일에 인증키를 저장하고 따로 관리하여야합니다.

---

## 프로젝트 구조

프로젝트 명: apptoaster(default)

- **app_core**:  
프로젝트의 기본 설정과 관련된 앱. 사전 설정 데이터 생성 및 스케줄러, 기본적인 설정과 관련된 테이블이 정의되어있습니다.
  - MODEL:
    - ACCOUNT (계정 정보)
      - *id PK
      - *username 사용자 아이디
      - *password 사용자 비밀번호
      - *first_name 사용자 실명
      - *last_name 사용자 닉네임
      - *email 이메일
      - *is_active 계정 활성 여부 (True, False)
      - *is_staff 관리자 계정 여부 (True, False)
      - *is_superuser 관리자 계정 여부 (True, False)
      - *date_joined 가입일
      - *last_login 마지막 로그인
      - *groups 사용자 계정 그룹 FK(user, dame, partner, subsupervisor, supervisor)
      - status 계정 상태(active, pending, deleted, blocked, banned)
      - note 관리자 노트
      - coupon_point 쿠폰 포인트
      - level_point 레벨 포인트
      - tel 연락처
      - address 주소
      - subsupervisor_permissions 부관리자 권한
      - bookmarked_places FK 북마크된 여행지 게시글
      - level FK 사용자 레벨
    - GROUP (그룹)
      - name 그룹명
      - permissions FK (사용안함)
    - ACTIVITY (계정 활동)
      - id PK
      - account FK
      - message 계정 활동 메세지
      - point_change 포인트 변동 내역
      - created_at 생성일
    - LEVEL_RULE (레벨 규칙)
      - level PK
      - image 레벨 뱃지 이미지
      - text 레벨 뱃지 텍스트
      - text_color 레벨 뱃지 텍스트 색상
      - background_color 레벨 뱃지 배경 색상
      - required_point 레벨 요구 포인트
    - CATEGORY (여행지 게시글 카테고리)
      - id PK
      - parent_category FK
      - name 카테고리 이름
      - display_weight 표시 순서
    - BOARD (게시판)
      - id PK
      - parent_board FK
      - display_groups FK
      - enter_groups FK
      - write_groups FK
      - comment_groups FK
      - name 게시판 이름
      - board_type 게시판 타입
      - display_weight 표시 순서
    - POST (게시글)
      - id PK
      - author FK
      - boards FK
      - review_post FK
      - place_info FK
      - title 게시글 제목
      - content 게시글 내용
      - image_paths 대표 이미지 경로
      - view_count 조회수
      - like_count 추천수
      - search_weight 검색 가중치
      - created_at 작성일
    - PLACE_INFO (여행지 정보)
      - id PK
      - post FK
      - categories FK
      - address 주소
      - location_info 위치 정보
      - open_info 운영 정보
      - ad_start_at 광고 시작일
      - ad_end_at 광고 종료일
      - status 상태
      - note 관리자 메모
    - COMMENT (댓글)
      - id PK
      - author FK
      - parent_comment FK
      - post FK
      - content 댓글 내용
      - created_at 작성일시
    - COUPON (쿠폰)
      - code PK
      - create_account FK
      - own_accounts FK
      - name 쿠폰 이름
      - content 쿠폰 내용
      - image 이미지
      - required_point 요구 포인트
      - expire_at 만료 일시
      - created_at 발급 일시
      - status 상태
      - note 관리자 메모
    - MESSAGE (메세지)
      - id PK
      - to FK
      - sender FK
      - include_coupon FK
      - title 메세지 제목
      - content 메세지 내용
      - is_read 읽음 여부
      - created_at 발송 일시
    - UPLOAD (업로드)
      - id PK
      - file 파일
    - SERVER_SETTING (서버 설정)
      - name PK
      - value 값
    - SERVER_LOG (서버 기록)
      - id PK
      - content 매새자
      - created_at 생성 일시
    - BANNER (배너)
      - id PK
      - location 배너 위치
      - image 배너 이미지
      - link 링크
      - display_weight 배너 표시 순서
- **app_api**:  
API 요청 주소와 해당 요청에 대한 처리가 정의되어있는 앱. 별도로 정의된 테이블은 없습니다.
- **app_user**:  
사용자 앱. 기본 사용자 페이지들에 대한 주소와 해당 요청에 대한 처리가 정의되어있는 앱.
  - PATH:
    - /(메인 페이지)
    - /signup(회원가입)
    - /find_account(계정 찾기)
    - /profile(프로필)
    - /activity(활동 기록)
    - /bookmark(북마크)
    - /contact(제휴문의)
    - /terms(이용약관)
- **app_partner**:  
파트너 앱. 파트너 관리자 페이지들에 대한 주소와 해당 요청에 대한 처리가 정의되어있는 앱.  
  - PATH:
    - /partner(파트너 관리자)
    - /partner/write_post(여행지 게시글 작성)
    - /partner/rewrite_post(여행지 게시글 수정)
    - /partner/coupon(파트너 쿠폰 관리)
- **app_supervisor**:  
사이트 관리자 앱. 사이트 관리자 페이지들에 대한 주소와 해당 요청에 대한 처리가 정의되어있는 앱.  
  - PATH:
    - /supervisor(관리자 메인)
    - /supervisor/account(계정 관리)
    - /supervisor/post(게시글 관리)
    - /supervisor/ad_post(여행지 관리)
    - /supervisor/coupon(쿠폰 관리)
    - /supervisor/message(쪽지 관리)
    - /supervisor/banner(배너 관리)
    - /supervisor/level(레벨 정책 관리)
    - /supervisor/setting(사이트 설정 관리)
- **app_post**:  
게시글 앱. 게시글과 관련된 페이지들의 주소와 해당 요청에 대한 처리가 정의되어있는 앱.
/post(게시판) 페이지는 공지사항, 이벤트, 후기, 여행지 게시판을 제외한 나머지 게시판의 경우, 이 페이지에서 처리함. 여행지 게시글의 경우 파트너 여행지 게시글 작성 페이지에서 작성. 공지사항 작성은 일반 게시글 작성 페이지에서 작성 가능.
  - PATH:
    - /post(게시판)
    - /post/write_post(글 작성)
    - /post/rewrite_post(글 수정)
    - /post/post_view(글 보기)
    - /post/notice(공지사항 게시판)
    - /post/event(이벤트 게시판)
    - /post/write_event(이벤트 작성)
    - /post/rewrite_event(이벤트 수정)
    - /post/event_view(이벤트 보기)
    - /post/attendance(출석체크)
    - /post/greeting(가입인사)
    - /post/review(후기 게시판)
    - /post/write_review(후기 작성)
    - /post/rewrite_review(후기 수정)
    - /post/review_view(후기 보기)
    - /post/travel(여행지 게시판)
    - /post/travel_view(여행지 보기)
- **app_coupon**:  
쿠폰 앱. 쿠폰과 관련된 페이지들의 주소와 해당 요청에 대한 처리가 정의되어있는 앱.
  - PATH:
    - /coupon(사용자 쿠폰 조회) user 및 dame 게정만 이용 가능. 파트너는 /partner/coupon 페이지. 관리자는 /supervisor/coupon 페이지를 이용함.
- **app_message**:  
메세지 앱. 쪽지와 관련된 페이지들의 주소와 해당 요청에 대한 처리가 정의되어있는 앱.  
  - PATH:
    - /message(쪽지) 관리자의 경우 /supervisor/message 페이지를 이용.

---

## 기능설명

- **사용자 계정**:  
사용자 계정은 일반 사용자(user), 여성 회원(dame), 파트너 회원(partner), 사이트 상위 관리자(supervisor), 사이트 하위 관리자(sub_supervisor), 데이터베이스 관리자(admin)로 구분합니다.
일반적인 회원가입으로는 일반 사용자, 여성 회원, 파트너 회원이 가입 가능하며, 본인 인증 또는 연락처, 이메일 인증 등의 가입 시 인증 수단은 사용하지 않습니다.
여성 회원 및 파트너 회원은 가입 시 가입 대기중(pending) 상태로 가입되며, 여성 회원은 가입 대기중 상태에서는 일반 회원과 동일한 권한을 가집니다. 파트너 회원은 가입 대기중 상태로는 어떤 작업도 불가능합니다. 가입 대기중 상태는 사이트 관리자 페이지에서 사용자 상태 변경을 통해 수정 가능합니다.
사용자는 다음과 같은 정보를 가집니다. 아이디, 비밀번호, 닉네임, 계정 타입, 상태(active, pending, deleted, banned), 가입 날짜, 마지막 로그인 날짜, 레벨 포인트, 쿠폰 포인트, 사용자 레벨, 북마크된 게시글 아이디들, 파트너 연락처, 파트너 주소, 파트너 카테고리 아이디들, 사이트 부 관리자 권한들(user, post, banner, level, coupon, message, level, setting), 관리자 메모
Django의 기본 User 테이블을 상속하여 사용합니다.

- **사용자 레벨**:  
회원가입, 게시글 작성, 댓글 작성, 리뷰 작성, 출석 시 레벨 포인트를 획득합니다. 획득한 레벨 포인트는 레벨 테이블의 필요 레벨 포인트에 따라서 사용자 레벨값을 수정합니다. 기본적으로 레벨은 올라가기만 하며, 사이트 관리자가 직접 수정하지 않는 이상 내려가지 않습니다. 관리자는 사용자 레벨 정보를 수정하거나 새로운 레벨을 만들 수 있습니다. 레벨 삭제는 불가능합니다.
레벨은 다음과 같은 정보를 가집니다. 레벨, 레벨 이름, 레벨 뱃지 배경색, 레벨 뱃지 글자색, 레벨업에 필요한 포인트

- **파트너 계정**:  
파트너 계정은 사이트 회원가입을 통해서 파트너 계정 가입 신청을 할 수 있습니다. 파트너 계정은 일반 사용자 계정(user, dame)과는 다르게 파트너 연락처와 파트너 주소, 파트너 카테고리 아이디들 값이 가입 시 추가로 필요하며, 여성 회원(dame)과 마찬가지로 가입 시 가입 대기중(pending) 상태로 가입됩니다. 다만 여성 회원(dame)과는 다르게 가입 대기중 상태에서는 아무 작업도 할 수 없습니다.
파트너 계정은 1개의 여행지 게시글을 작성할 수 있습니다. 여행지 게시글은 게시글 테이블과 게시글 광고 테이블로 구분됩니다. 게시글 광고에는 광고 ID, 여행지 게시글 ID, 광고 상태(active, expired), 광고 시작일, 광고 종료일이 있습니다.
게시글 테이블은 다음과 같은 필드로 구분됩니다. 게시글 ID, 이미지, 리뷰 여행지 ID(리뷰 게시글만 해당), 제목, 내용, 작성일, 작성자 ID
그 외 쿠폰을 생성하고 수정하며 다른 사용자에게 쿠폰을 전달할 수 있는 기능을 제공합니다.
파트너 계정은 가입 시 파트너 카테고리가 필요합니다. 주로 파트너의 등록 여행지 사업 범주를 의미합니다.(예: 레스토랑 및 카페 > 양식 레스토랑 > 파스타) 파트너 카테고리 트리 구조는 최대 4단계까지만 내려갈 수 있으며, 파트너 카테고리 ID, 카테고리명, 하위 카테고리 아이디들로 구분됩니다.

- **게시판 및 게시글**:  
게시판은 게시판 폴더와 게시판으로 구분합니다. 게시판 폴더는 다른 게시판들을 담을 수 있으며, 별도의 게시판으로 취급하지 않습니다.(다른 게시판들을 담는데만 사용). 게시판은 게시판 입장 권한, 게시판 내 게시글 읽기 권한, 게시글 작성 권한, 댓글 작성 권한과 게시판 이름, 게시판 타입(게시판 폴더, 여행지, 이벤트, 리뷰, 일반 게시판 타입)과 하위 게시판 아이디들로 구분되며, 각 게시판 타입별로 게시글이 다르게 표시됩니다. 게시판 트리 구조(하위 게시판 구조)는 최대 4단계까지만 내려갈 수 있습니다.
게시글은 ToastfulEditor를 이용해서 작성 및 표시하며 제목, 내용(ToastfulEditor), 첨부 이미지(이벤트, 여행지 게시글, 리뷰 게시글에만 사용), 리뷰 대상 게시글 아이디(리뷰 게시글만 해당), 리뷰 랭킹(리뷰 게시글만 해당), 북마크 아이디들, 조회 아이디들과 작성자 아이디, 작성일 필드가 있습니다.
댓글은 작성자 아이디, 댓글 내용, 작성일, 하위 댓글 아이디 필드로 구분됩니다. 댓글에는 대댓글을 작성할 수 있으며, 대댓글에는 다시 대댓글을 작성할 수 없습니다.(댓글 > 대댓글 이렇게까지만 가능). 댓글 및 게시글은 관리자 또는 작성자만 삭제하거나 수정할 수 있습니다.(댓글은 삭제만 가능)
그 외 출석체크와 가입인사 게시판이 있습니다. 출석체크는 오늘 날짜의 출석 게시판의 게시글의 댓글을 작성하는식으로 구현됩니다. 가입인사는 가입인사 게시판의 게시글에 댓글을 작성하는 식으로 구협됩니다. 다만 출석체크 페이지는 페이지네이션을 구현하지 않으나, 가입인사의 경우, 페이지네이션 기능을 사용합니다.

- **쿠폰**:  
파트너 계정과 관리자 계정은 쿠폰을 생성할 수 있습니다. 각 쿠폰에는 쿠폰 코드, 쿠폰 이름, 쿠폰 설명, 대표 이미지, 쿠폰 사용 시 필요 포인트, 쿠폰 생성자(파트너 또는 관리자), 대상 여행지 게시글 및 쿠폰 소유자 아이디들(user, dame 아이디들) 및 쿠폰 생성일로 구분되며 쪽지에 쿠폰 첨부를 통해서 사용자에게 전달할 수 있습니다.
쿠폰 파트너 > 쿠폰 관리에서 쿠폰 사용 처리를 할 수 있으며 만약 쿠폰에 쿠폰 사용 시 필요 포인트가 설정되어있다면 쿠폰 사용 처리 시 사용자의 쿠폰 포인트가 차감됩니다. 만약 사용자 쿠폰 포인트가 부족하다면 쿠폰 사용처리가 불가합니다.
쿠폰 생성자는 언제든지 쿠폰 내용을 수정할 수 있습니다.
쿠폰이 사용처리되거나 쿠폰을 회수한 경우, 사용 가능한 쿠폰 목록에서 해당 쿠폰이 제거되며 쿠폰 기록에서 쿠폰을 확인할 수 있게 됩니다.
쿠폰 기록에는 쿠폰 상태가 포함됩니다. 쿠폰 상태는 사용, 만료, 삭제의 상태를 가집니다.

- **리뷰 게시글**:  
리뷰 게시글은 여행지 게시글 페이지에서 리뷰 작성하기를 통해 작성할 수 있습니다. 리뷰 게시글 작성 시 리뷰 게시글 작성 포인트를 얻을 수 있습니다. 리뷰 게시글은 여행지 게시글과 마찬가지로 대표 이미지들을 별도로 설정할 수 있으며, 여행지 게시글과 연결됩니다.
리뷰 게시글은 조회수, 북마크수, 댓글수, 가중치(직접 설정 가능)를 바탕으로 일간, 주간, 월간 리뷰 랭킹을 생성합니다.
주간 및 월간 랭킹은 스케줄러에서 리뷰 점수를 책정하여 계산해 표시합니다.
일간 랭킹은 조회수를 기반으로 생성합니다.

- **광고 배너**:  
광고 배너는 메인 페이지에만 표시합니다. 클릭 시 새 탭을 통해 외부 링크를 엽니다.(target=_blank) 광고 배너는 상단 및 사이드(모바일은 하단) 위치에 있을 수 있으며, 사이트 관리자 > 배너 설정을 통해 배너를 수정하거나 새 배너를 생성할 수 있습니다.
배너는 다음과 같은 정보를 가집니다. 배너 이미지, 외부 링크, 위치(상단, 측면)

- **사이트 관리자(Supervisor)**:  
사이트 관리자 게정은 상위 사이트 관리자 계정과 하위 사이트 관리자 계정으로 구분됩니다.
상위 사이트 관리자 계정은 1개만 존재하며 서버 초기화 시 자동으로 생성됩니다.
하위 관리자 계정은 상위 관리자 계정이 생성할 수 있으며, 사용자 관리, 게시글 관리, 쿠폰 관리, 쪽지 관리, 배너 관리, 사이트 설정 관리 권한을 직접 설정할 수 있습니다.
모든 사이트 관리자는 같은 쪽지함을 공유합니다. 사용자 계정에서 사이트 관리자에게 문의 쪽지를 보내면 모든 사이트 관리자가(쪽지 권한이 있는) 확인할 수 있습니다.

- **데이터베이스 관리자(Admin)**:  
데이터베이스 관리자는 Django Admin 계정을 의미합니다. 서버 생성 시 자동으로 생성되며 사이트 관리자는 Admin 접속 권한을 가지지 않습니다.
데이터베이스 관리자 계정은 사이트 관리 권한을 가지지 않습니다.

--- 

## 색상

- **주 색상**:
#FCE4EC
- **부 색상**:
#FFF9F0
- **회색 색상**:
#808080
- **footer 배경색**:
#E3F2FD
- **footer 폰트색**:
#0D47A1