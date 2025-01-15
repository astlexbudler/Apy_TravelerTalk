import datetime
import random
import string
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, logout, get_user_model
from django.db.models import Q

from app_core import models as core_mo
from app_user import models as user_mo
from app_partner import models as partner_mo
from app_supervisor import models as supervisor_mo
from app_post import models as post_mo
from app_message import models as message_mo
from app_coupon import models as coupon_mo

from app_core import daos as core_dao

# 사용자의 붇마크 게시글 가져오기
# 사용자가 로그인되어있지 않거나, 잘못된 사용자일 경우, 빈 리스트 반환
def get_user_bookmarks(user):
  bookmarks = []

  # 사용자 확인
  if user.is_authenticated:

    # 사용자 계정에 저장된 붇마크 확인
    bks = str(user.user_bookmarks).split(',')
    for bookmark_id in bks:
      if bookmark_id: # 북마크가 존재하는 경우

        # 북마크 게시글 가져오기
        bookmark_po = post_mo.POST.objects.filter(id=int(bookmark_id)).first()
        if not bookmark_po: # 북마크 게시글이 존재하지 않는 경우
          # 잘못된 붇마크를 삭제하고 루프 건너뛰기
          user.user_bookmarks = user.user_bookmarks.replace(bookmark_id + ',', '')
          user.save()
          continue

        # 북마크 게시글의 작성자 정보 가져오기
        bookmark_po_au = get_user_model().objects.filter(
          username=bookmark_po.author_id,
          ).first()
        if not bookmark_po_au:
          # 잘못된 붇마크를 삭제하고 루프 건너뛰기
          user.user_bookmarks = user.user_bookmarks.replace(bookmark_id + ',', '')
          user.save()
          continue

        # 게시글 작성자 레벨 정보
        level = core_dao.get_user_level(bookmark_po_au)

        # 게시글 작성자 정보
        author = {
          'id': bookmark_po_au.username,
          'nickname': bookmark_po_au.first_name,
          'level': level,
          'account_type': bookmark_po_au.account_type,
        }

        # 북마크 게시글 정보
        bookmarks.append({
          'id': bookmark_po.id,
          'title': bookmark_po.title,
          'author': author,
          'created_dt': bookmark_po.created_dt,
          'view_count': len(str(bookmark_po.views).split(',')) - 1,
          'like_count': len(str(bookmark_po.bookmarks).split(',')) - 1,
          'comment_count': post_mo.COMMENT.objects.filter(post_id=bookmark_po.id).count(),
        })

  return bookmarks

# 게시판 트리 가져오기
# 트리는 최대 4단계까지 내려갈 수 있음.
# 각 게시판에는 display_permissions, enter_permissions, write_permissions, comment_permissions가 있음.
# display_permissions: 게시판을 볼 수 있는 권한
# enter_permissions: 게시판글을 볼 수 있는 권한
# write_permissions: 게시글을 작성할 수 있는 권한
# comment_permissions: 댓글을 작성할 수 있는 권한
def get_boards():
  boards = post_mo.BOARD.objects.all()
  board_dict = {
    board.name: {
      'id': board.id,
      'name': board.name,
      'post_type': board.post_type,
      'display_permissions': board.display_permissions,
      'enter_permissions': board.enter_permissions,
      'write_permissions': board.write_permissions,
      'comment_permissions': board.comment_permissions,
      'children': [],
    } for board in boards if board.parent_id == ''
  }
  for board in boards:
    if board.parent_id:
      if board_dict.get(post_mo.BOARD.objects.get(id=board.parent_id).name):
        board_dict[post_mo.BOARD.objects.get(id=board.parent_id).name]['children'].append({
          'id': board.id,
          'name': board.name,
          'post_type': board.post_type,
          'display_permissions': board.display_permissions,
          'enter_permissions': board.enter_permissions,
          'write_permissions': board.write_permissions,
          'comment_permissions': board.comment_permissions,
          'children': [],
        })
      else:
        loop = True
        for key in board_dict.keys():
          for child in board_dict[key]['children']:
            # 3단계 게시판
            if not loop:
              break
            if str(child['id']) == str(board.parent_id):
              child['children'].append({
                'id': board.id,
                'name': board.name,
                'post_type': board.post_type,
                'display_permissions': board.display_permissions,
                'enter_permissions': board.enter_permissions,
                'write_permissions': board.write_permissions,
                'comment_permissions': board.comment_permissions,
                'children': [],
              })
              loop = False
            # 4단계 게시판
            if loop:
              for grandchild in child['children']:
                if not loop:
                  break
                if str(grandchild['id']) == str(board.parent_id):
                  grandchild['children'].append({
                    'id': board.id,
                    'name': board.name,
                    'post_type': board.post_type,
                    'display_permissions': board.display_permissions,
                    'enter_permissions': board.enter_permissions,
                    'write_permissions': board.write_permissions,
                    'comment_permissions': board.comment_permissions,
                    'children': [],
                  })
                  loop = False
  boards = []
  for child in board_dict.keys():
    boards.append(board_dict[child])

  return boards

# 베스트 리뷰 미리보기 가져오기
# 미리보기는 전체 기간을 기분으로 weight가 높은 5개의 리뷰글을 가져옴.
def get_best_review_preview():

  # 베스트 리뷰글 가져오기
  # 기간은 상관 없음
  best_reviews = []
  review_board_id = post_mo.BOARD.objects.get( # 리뷰 게시판 아이디 가져오기
    post_type='review',
  ).id
  ps = post_mo.POST.objects.filter( # 리뷰 게시판에서 베스트 리뷰글 가져오기(5개)
    board_id=review_board_id,
  ).order_by('-weight')[:5] # weight는 스케줄러에서 업데이트됨.
  for post in ps:

    # 게시글 작성자 가져오기
    at = get_user_model().objects.filter(
      username=post.author_id,
    ).first()
    if not at:
      continue

    # 게시글 작성자 레벨 정보
    lv = core_mo.LEVEL_RULE.objects.get(level=at.user_level)
    level = {
      'level': lv.level,
      'text_color': lv.text_color,
      'background_color': lv.background_color,
      'name': lv.name,
    }

    # 게시글 직상지 정보
    author = {
      'id': at.username,
      'nickname': at.first_name,
      'account_type': at.account_type,
      'status': at.status,
      'level': level,
    }

    # 게시글 타겟 게시물 가져오기
    target_po = post_mo.POST.objects.filter(
      id=post.target_post_id,
    ).first()
    if not target_po:
      continue

    # 게시글 타겟 게시물 작성자 정보
    target_po_au = get_user_model().objects.filter(
      status='active',
      username=target_po.author_id,
    ).first()
    if not target_po_au:
      continue
    target_author = {
      'id': target_po_au.username,
      'partner_categories': target_po_au.partner_categories,
    }

    # 타겟 게시물정보
    target_post = {
      'id': target_po.id,
      'title': target_po.title,
      'author': target_author,
    }

    # 리뷰 게시글 정보
    best_reviews.append({
      'id': post.id,
      'title': post.title,
      'author': author,
      'target_post': target_post,
      'created_dt': post.created_dt,
      'view_count': len(str(post.views).split(',')) - 1,
      'like_count': len(str(post.bookmarks).split(',')) - 1,
    })

  return best_reviews

def get_post_search(posts):
  results = []
  for post in posts:

    # 게시판 정보 가져오기
    # 게시판은 여러 개에 속할 수 있음.(예: 커뮤니티 > 공개 게시판 > 자유게시판 등)
    boards = []
    for b in str(post.board_id).split(','):
      if b == '':
        continue
      board = post_mo.BOARD.objects.get(id=b)
      boards.append({
        'id': board.id,
        'name': board.name,
      })

    # 게시글 작성자 가져오기
    at = get_user_model().objects.filter(
      Q(status='active') | Q(status='pending'), # 사용자 상태가 active 또는 pending인 경우에만 가져옴.
      username=post.author_id,
    ).first()
    if not at: # 작성자를 확인할 수 없는 경우, continue
      continue

    # 게시글 작성자가 사용자인 경우
    if any(at.account_type == s for s in ['user', 'dame']):
      lv = core_mo.LEVEL_RULE.objects.get(level=at.user_level)
      level = {
        'level': lv.level,
        'text_color': lv.text_color,
        'background_color': lv.background_color,
        'name': lv.name,
      }
      author = {
        'id': at.username,
        'nickname': at.first_name,
        'account_type': at.account_type,
        'status': at.status,
        'level': level,
      }

    # 게시글 작성자가 파트너인 경우
    elif at.account_type == 'partner':
      author = {
        'id': at.username,
        'nickname': at.first_name,
        'account_type': at.account_type,
        'status': at.status,
        'partner_categories': at.partner_categories,
        'partner_address': at.partner_address,
      }

    else: # 그 외의 경우, 기본 정보만 가져옴.
      author = {
        'id': at.username,
        'nickname': at.first_name,
        'account_type': at.account_type,
        'status': at.status,
      }

    # 게시글 정보
    post = {
      'id': post.id,
      'boards': boards, # 게시글이 속한 게시판 정보
      'title': post.title,
      'author': author, # 작성자 정보
      'created_dt': post.created_dt,
      'view_count': len(str(post.views).split(',')) - 1, # 조회수
      'like_count': len(str(post.bookmarks).split(',')) - 1, # 북마크한 사용자 수
      'comment_count': post_mo.COMMENT.objects.filter(post_id=post.id).count(),
    }
    results.append(post)

  return results

def get_post_comments(post_id):
  comments = []
  cts = post_mo.COMMENT.objects.filter(
    post_id=post_id,
  ).order_by('created_dt')
  for comment in cts:

    # 댓글 작성자 정보 가져오기
    at = get_user_model().objects.filter(
      Q(status='active') | Q(status='pending'), # 사용자 상태가 active 또는 pending인 경우에만 가져옴.
      username=comment.author_id,
    ).first()
    if not at: # 작성자를 확인할 수 없는 경우, continue
      continue

    # 댓글 작성자가 사용자인 경우
    if any(at.account_type == s for s in ['user', 'dame']):
      lv = core_mo.LEVEL_RULE.objects.get(level=at.user_level)
      level = {
        'level': lv.level,
        'text_color': lv.text_color,
        'background_color': lv.background_color,
        'name': lv.name,
      }
      author = {
        'id': at.username,
        'nickname': at.first_name,
        'account_type': at.account_type,
        'status': at.status,
        'level': level,
      }

    else: # 그 외의 경우, 기본 정보만 가져옴.
      author = {
        'id': at.username,
        'nickname': at.first_name,
        'account_type': at.account_type,
        'status': at.status,
      }

    # sub_comments 정보 가져오기
    sub_comments = []
    for sub_comment in post_mo.COMMENT.objects.filter(
      target_comment_id=comment.id,
    ).order_by('created_dt'):
      sub_author = get_user_model().objects.filter(
        Q(status='active') | Q(status='pending'), # 사용자 상태가 active 또는 pending인 경우에만 가져옴.
        username=sub_comment.author_id,
      ).first()
      if not sub_author:
        continue
      if any(sub_author.account_type == s for s in ['user', 'dame']):
        lv = core_mo.LEVEL_RULE.objects.get(level=sub_author.user_level)
        level = {
          'level': lv.level,
          'text_color': lv.text_color,
          'background_color': lv.background_color,
          'name': lv.name,
        }
        sub_author = {
          'id': sub_author.username,
          'nickname': sub_author.first_name,
          'account_type': sub_author.account_type,
          'status': sub_author.status,
          'level': level,
        }
      else:
        sub_author = {
          'id': sub_author.username,
          'nickname': sub_author.first_name,
          'account_type': sub_author.account_type,
          'status': sub_author.status,
        }
      sub_comments.append({
        'id': sub_comment.id,
        'author': sub_author,
        'content': sub_comment.content,
        'created_dt': sub_comment.created_dt,
      })

    # 댓글 정보
    comment = {
      'id': comment.id,
      'author': author, # 작성자 정보
      'content': comment.content,
      'created_dt': comment.created_dt,
      'sub_comments': sub_comments,
    }
    comments.append(comment)

  return comments

def get_reviews(reviews):
  results = []

  for review in reviews:
    
    # 리뷰 작성자 정보 가져오기
    at = get_user_model().objects.filter(
      Q(status='active') | Q(status='pending'), # 사용자 상태가 active 또는 pending인 경우에만 가져옴.
      username=review.author_id,
    ).first()
    if not at: # 작성자를 확인할 수 없는 경우, continue
      continue

    # 리뷰 작성자는 모두 사용자
    lv = core_mo.LEVEL_RULE.objects.get(level=at.user_level)
    level = {
      'level': lv.level,
      'text_color': lv.text_color,
      'background_color': lv.background_color,
      'name': lv.name,
    }

    # 리뷰 작성자 정보
    author = {
      'id': at.username,
      'nickname': at.first_name,
      'account_type': at.account_type,
      'status': at.status,
      'level': level,
    }

    # 리뷰 타겟 게시물 가져오기
    target_po = post_mo.POST.objects.filter(
      id=review.target_post_id,
    ).first()
    if not target_po:
      continue

    # 리뷰 타겟 게시물 작성자는 모두 파트너
    target_po_au = get_user_model().objects.filter(
      status='active',
      username=target_po.author_id,
    ).first()
    if not target_po_au:
      continue
    target_author = {
      'id': target_po_au.username,
      'nickname': target_po_au.first_name,
      'partner_categories': target_po_au.partner_categories,
      'partner_address': target_po_au.partner_address,
    }

    # 리뷰 타겟 게시물 정보
    target_post = {
      'id': target_po.id,
      'title': target_po.title,
      'author': target_author,
    }

    # 리뷰 정보
    review = {
      'id': review.id,
      'title': review.title,
      'images': str(review.images).split(','),
      'created_dt': review.created_dt,
      'author': author,
      'target_post': target_post,
      'created_dt': review.created_dt,
      'view_count': len(str(review.views).split(',')) - 1,
      'like_count': len(str(review.bookmarks).split(',')) - 1,
      'comment_count': post_mo.COMMENT.objects.filter(post_id=review.id).count(),
    }
    results.append(review)

  return results