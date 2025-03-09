from django.urls import path

from . import views as v

urlpatterns = [

  # views as v
  # 게시판 페이지
  # 표준 게시판의 게시글 목록 및 검색 내역 제공
  # 따로 게시판 템플릿이 존재하는 경우, 해당 게시판 페이지로 redirect
  # 게시판 접근 권한 확인
  path('', v.poat_board, name='post_board'),

  # 출석 게시판 페이지
  # 출석 게시글 목록 및 검색 내역 제공
  # 시스템에서 작성한 출석 게시글의 댓글 목록을 가져옴
  # 예: 2024-01-01 출석 게시글의 댓글 목록 확인. 게시글이 없는 경우, 오늘 날짜의 게시글 생성 후 가져옴
  # 출석 1등은 출석 포인트의 2배 지급, 2등은 1.5배, 3등은 1.2배
  path('attendance', v.attendance, name='attendance'),

  # 가입인사 게시판 페이지
  # 가입인사 게시글 목록 및 검색 내역 제공
  # 가입인사 게시글의 댓글 목록을 가져옴
  # 가입 인사는 계정당 한번만 가능. greeting_comment_exist 필드로 확인
  path('greeting', v.greeting, name='greeting'),

  # 리뷰 게시판 페이지
  # 리뷰 게시글 목록 및 검색 내역 제공
  path('review', v.review, name='review'),

  # 광고 게시판 페이지
  # 광고 게시글 목록 및 검색 내역 제공
  path('travel', v.travel, name='travel'),

  # 게시글 작성 페이지
  # 표준 게시글 작성 폼 제공
  # title, content 필드 제공
  # 게시글 작성 권한 확인
  path('write_post', v.write_post, name='write_post'),

  # 게시글 수정 페이지
  # 표준 게시글 수정 폼 제공
  # title, content 필드 제공
  # 게시글 작성자 맟 관리자만 수정 가능(보조 관리자의 경우 게시글 관리 권한 확인)
  path('rewrite_post', v.rewrite_post, name='rewrite_post'),

  # 게시글 상세 페이지
  # 표준 게시글의 상세 정보 제공
  # 게시글 내용 및 댓글 목록 확인
  # 게시글 작성자의 경우 게시글 수정 버튼 표시
  # 게시글 조회 권한 확인
  path('post_view', v.post_view, name='post_view'),

]
