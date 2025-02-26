from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from app_core import models, daos
from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, logout, login
import datetime
import random
import string

####################
# APIS
# *데이터베이스 처리 로직은 app_core.daos.py에 구현되어있습니다. 여기서는 API 로직만 구현합니다.
# *여기서는 권한, 사용자 요청 값 확인 등의 작업만 수행합니다.
# def api_login(request): 로그인 api
# def api_logout(request): 로그아웃 api
# def api_file_upload(request): 파일 업로드 api
# def api_receive_coupon(request): 쿠폰 받기 api
# def api_like_post(request): 게시글 좋아요 토글 api
# class api_account(APIView): 사용자 REST API
# - GET: search 사용자. id, nickname, any로 검색 가능. (id, nickname, status 반환)
# - POST: create 사용자. id, password, nickname, partner_name, email(선택), account_type(user, dame, partner, subsupervisor)를 받아 사용자 생성.
# - PATCH: update 사용자. password, nickname, partner_name, email, status, note, subsupervisor_permissions를 받아 사용자 수정.
# class api_message(APIView): 메세지 REST API
# - GET: 메세지 읽음 처리. message_id를 받아 메세지의 is_read를 True로 변경.
# - POST: create 메세지. sender, receiver, title, content, image, include_coupon_code를 받아 메세지 생성.
# class api_comment(APIView): 댓글 REST API
# - POST: create 댓글. post_id, account_id, content을 받아 댓글 생성.
# - PATCH: update 댓글. comment_id, content를 받아 댓글 수정.
# - DELETE: delete 댓글. comment_id를 받아 댓글 삭제.
# class api_coupon(APIView): 쿠폰 REST API
# - GET: search 쿠폰. code를 받아 쿠폰 검색.
# - POST: create 쿠폰. code, title, content, image, expire_date, required_mileage, related_post_id를 받아 쿠폰 생성.
# - PATCH: update 쿠폰. code, title, content, image, expire_date, required_mileage, own_account_id, status를 받아 쿠폰 수정.

# 로그인 api
def api_login(request):

    # id, password를 받아 로그인 처리
    id = request.POST.get('id')
    password = request.POST.get('password')
    remember = request.POST.get('remember')
    print('id:', id, 'password:', password, 'remember:', remember)

    # 로그인 처리
    user = authenticate(username=id, password=password)

    if user is None: # 로그인 실패
        return JsonResponse({"success": False, 'status': 400, "message": "아이디 또는 비밀번호가 일치하지 않습니다."})
    else: # 로그인 성공
        login(request, user)

    return JsonResponse({"success": True, 'status': 200, "message": "로그인 성공", "data": user.status})

# 로그아웃 api
def api_logout(request):

    # 로그아웃 처리
    logout(request)

    return JsonResponse({"success": True, 'status': 200, "message": "로그아웃 성공"})

# 파일 업로드 api
def api_file_upload(request):

    # 로그인 여부 확인
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, 'status': 401, "message": "로그인이 필요합니다."})

    # 파일 업로드 처리
    file = request.FILES['file']

    # 응답
    file_path = daos.upload_file(file)
    response = {
        'path': 'media/' + file_path,
    }

    return JsonResponse({"success": True, 'status': 200, "message": "파일 업로드 성공", 'data': response})

# 쿠폰 받기 api
def api_receive_coupon(request):

    # 메세지 아이디 확인
    message_id = request.POST.get('message_id')
    account_id = request.user.id

    # 메세지 확인
    message = daos.select_message(message_id)
    if message['success'] == False:
        return JsonResponse({"success": False, 'status': 400, "message": message['message']})
    elif message['to_account']['id'] != account_id:
        return JsonResponse({"success": False, 'status': 400, "message": "본인에게만 쿠폰을 받을 수 있습니다."})
    elif message['include_coupon'] == None:
        return JsonResponse({"success": False, 'status': 400, "message": "쿠폰이 포함되어있지 않습니다."})

    # 쿠폰 받기
    daos.update_coupon(
        code=message['include_coupon']['code'],
        own_account_id=account_id
    )

    # 메세지에 담긴 쿠폰 삭제
    daos.update_message(message_id)

    return JsonResponse({"success": True, 'status': 200, "message": "쿠폰 받기 성공"})

# 게시글 좋아요 토글 api
def api_like_post(request):

    # 게시글 아이디 확인
    post_id = request.POST.get('post_id')

    # 로그인 여부 확인
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, 'status': 401, "message": "로그인이 필요합니다."})
    account_id = request.user.username

    # 게시글 확인
    post = daos.select_post(post_id)
    if post['success'] == False:
        return JsonResponse({"success": False, 'status': 400, "message": post['message']})

    # 게시글 타입 확인 후 좋아요 처리
    if post['place_info'] == None: # 세션으로 처리
        user_like_posts = request.session.get('like_post_ids', '')
        if str(post['id']) in user_like_posts:
            user_like_posts = user_like_posts.replace(str(post['id']) + ',', '')
            is_liked = False
        else:
            user_like_posts += str(post['id']) + ','
            is_liked = True
    else: # DB로 처리
        user_bookmark_posts = daos.select_account(account_id)['bookmark_posts']
        if str(post['id']) in user_bookmark_posts:
            user_bookmark_posts = user_bookmark_posts.replace(str(post['id']) + ',', '')
            is_liked = False
        else:
            user_bookmark_posts += str(post['id']) + ','
            is_liked = True

    # 게시글 업데이트
    if is_liked:
        like_count = int(post['like_count']) + 1
    else: # 좋아요 취소
        like_count = int(post['like_count']) - 1

    daos.update_post(
        post_id=post_id,
        like_count=like_count
    )

    # 응답
    response = {
        'is_liked': is_liked,
    }

    return JsonResponse({"success": True, 'status': 200, "message": "게시글 좋아요 토글 성공", 'data': response})

# 사용자 REST API
class api_account(APIView):
    # 사용자 검색 api(GET)
    def get(self, request, *args, **kwargs):

        # 사용자 검색
        id = request.query_params.get('id')
        nickname = request.query_params.get('nickname')
        any = request.query_params.get('any') # 닉네임 또는 아이디로 검색

        accounts = daos.search_accounts(
            username=id,
            nickname=nickname,
            any=any
        )

        return JsonResponse({"success": True, 'status': 200, "message": "사용자 조회 성공", 'data': accounts[0]})

    # 사용자 생성 api(POST)
    def post(self, request, *args, **kwargs):

        # 사용자 생성
        id = request.data.get('id')
        password = request.data.get('password')
        nickname = request.data.get('nickname')
        partner_name = request.data.get('partner_name')
        email = request.data.get('email')
        tel = request.data.get('tel')
        account_type = request.data.get('account_type')

        account = daos.create_account(
            username=id,
            password=password,
            first_name=nickname,
            last_name=partner_name,
            email=email,
            account_type=account_type,
            tel=tel
        )

        # 기본 게시글 생성
        if account_type == 'partner':
            board_ids = request.data.get('board_ids')
            category_ids = request.data.get('category_ids')
            address = request.data.get('address')
            post = daos.create_post(
                author_id=account['pk'],
                title='기본 여행지 게시글 제목',
                content='여행지 내용을 입력해주세요.',
                board_ids=board_ids,
            )
            daos.create_post_place_info(
                post_id=post['pk'],
                category_ids=category_ids,
                location_info='위치 안내 메세지를 입력해주세요.',
                open_info='영업 정보를 입력해주세요.',
                address=address,
                status='writing'
            )

        return JsonResponse({"success": True, 'status': 200, "message": "사용자 생성 성공", 'data': account['status']})

    # 사용자 수정 api(PATCH)
    def patch(self, request, *args, **kwargs):

        # 사용자 수정
        id = request.data.get('id')

        # 계정 확인
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, 'status': 401, "message": "로그인이 필요합니다."})
        account = daos.select_account(request.user.id)
        if request.user.username != id:
            if 'user' not in account['subsupervisor_permissions']:
                return JsonResponse({"success": False, 'status': 403, "message": "권한이 없습니다."})

        # 수정할 데이터
        password = request.data.get('password')
        nickname = request.data.get('nickname')
        partner_name = request.data.get('partner_name')
        email = request.data.get('email')
        if 'user' in account['subsupervisor_permissions']: # 사용자 수정 권한이 있는 경우
            exp = request.data.get('exp')
            mileage = request.data.get('mileage')
            status = request.data.get('status')
        if account['account_type'] == 'supervisor': # 최상위 관리자인 경우
            subsupervisor_permissions = request.data.get('subsupervisor_permissions') # ,로 구분된 문자열(user,post,coupon,setting..)

        daos.update_account(
            id=id,
            password=password,
            first_name=nickname,
            last_name=partner_name,
            email=email,
            exp=exp,
            mileage=mileage,
            status=status,
            subsupervisor_permissions=subsupervisor_permissions
        )

        return JsonResponse({"success": True, 'status': 200, "message": "사용자 수정 성공"})

# 메세지 REST API
class api_message(APIView):
    # 메세지 읽음 처리 api(GET)
    def get(self, request, *args, **kwargs):

        # 메세지 읽음 처리
        message_id = request.query_params.get('message_id')

        # 읽음 처리
        daos.update_message(message_id) # 메세지 읽음 처리

        return JsonResponse({"success": True, 'status': 200, "message": "메세지 읽음 처리 성공"})

    # 메세지 생성 api(POST)
    def post(self, request, *args, **kwargs):

        # 메세지 생성
        sender_id = request.data.get('sender_id')
        receiver_id = request.data.get('receiver_id')

        # 계정 확인
        if receiver_id != 'supervisor' and not request.user.is_authenticated:
            return JsonResponse({"success": False, 'status': 401, "message": "로그인이 필요합니다."})

        title = request.data.get('title')
        content = request.data.get('content') # wysiwig 사용
        image = request.data.get('image')
        include_coupon_code = request.data.get('include_coupon_code')

        # 메세지 생성
        response = daos.create_message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            title=title,
            content=content,
            image=image,
            include_coupon_code=include_coupon_code
        )

        if response['success']:
            return JsonResponse({"success": True, 'status': 200, "message": "메세지 생성 성공", 'pk': response['pk']})
        else:
            return JsonResponse({"success": False, 'status': 400, "message": "메세지 생성 실패", "errors": response['message']})

# 댓글 REST API
class api_comment(APIView):
    # 댓글 생성 api(POST)
    def post(self, request, *args, **kwargs):

        # 댓글 생성
        post_id = request.data.get('post_id')
        content = request.data.get('content')

        response = daos.create_comment(
            post_id=post_id,
            content=content
        )

        if response['success']:
            return JsonResponse({"success": True, 'status': 200, "message": "댓글 생성 성공"})
        else:
            return JsonResponse({"success": False, 'status': 400, "message": "댓글 생성 실패", "errors": response['message']})

    # 댓글 수정 api(PATCH)
    def patch(self, request, *args, **kwargs):

        # 댓글 수정
        comment_id = request.data.get('comment_id')
        content = request.data.get('content')

        # 댓글 수정
        response = daos.update_comment(
            comment_id=comment_id,
            content=content
        )

        if response['success']:
            return JsonResponse({"success": True, 'status': 200, "message": "댓글 수정 성공"})
        else:
            return JsonResponse({"success": False, 'status': 400, "message": "댓글 수정 실패", "errors": response['message']})

    # 댓글 삭제 api(DELETE)
    def delete(self, request, *args, **kwargs):

        # 댓글 삭제
        comment_id = request.query_params.get('comment_id')

        # 로그인 여부 확인
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, 'status': 401, "message": "로그인이 필요합니다."})

        # 댓글 삭제
        response = daos.delete_comment(
            comment_id=comment_id
        )

        if response['success']:
            return JsonResponse({"success": True, 'status': 200, "message": "댓글 삭제 성공"})
        else:
            return JsonResponse({"success": False, 'status': 400, "message": "댓글 삭제 실패", "errors": response['message']})

# 쿠폰 REST API
class api_coupon(APIView):
    # 쿠폰 조회 api(GET)
    def get(self, request, *args, **kwargs):

        # 쿠폰 조회
        code = request.query_params.get('code')
        if not code:
            return JsonResponse({"success": False, "status": 400, "message": "쿠폰 코드가 필요합니다."})

        response = daos.select_all_coupons(
            code=code
        )

        return JsonResponse({"success": True, 'status': 200, "message": "쿠폰 조회 성공", 'data': response})

    # 쿠폰 생성 api(POST)
    def post(self, request, *args, **kwargs):

        # 쿠폰 생성
        code = request.data.get('code')
        related_post_id = request.data.get('related_post_id')
        name = request.data.get('name')
        content = request.data.get('content') # wysiwig 사용
        image = request.data.get('image')
        expire_at = request.data.get('expire_at')
        required_mileage = request.data.get('required_mileage')

        # 로그인 여부 확인
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, 'status': 401, "message": "로그인이 필요합니다."})
        create_account_id = request.user.id

        response = daos.create_coupon(
            account_id=create_account_id,
            code=code,
            related_post_id=related_post_id,
            name=name,
            content=content,
            image=image,
            expire_at=expire_at,
            required_mileage=required_mileage
        )

        if response['success']:
            return JsonResponse({"success": True, 'status': 200, "message": "쿠폰 생성 성공", 'pk': response['pk']})
        else:
            return JsonResponse({"success": False, 'status': 400, "message": "쿠폰 생성 실패", "errors": response['message']})

    # 쿠폰 수정 api(PATCH)
    def patch(self, request, *args, **kwargs):

        # 쿠폰 수정
        code = request.data.get('code')
        name = request.data.get('name')
        content = request.data.get('content') # wysiwig 사용
        image = request.data.get('image')
        expire_at = request.data.get('expire_at')
        required_mileage = request.data.get('required_mileage')
        own_account_id = request.data.get('own_account_id')
        status = request.data.get('status')
        note = request.data.get('note')

        # 쿠폰 수정
        response = daos.update_coupon(
            code=code,
            name=name,
            content=content,
            image=image,
            expire_at=expire_at,
            required_mileage=required_mileage,
            own_account_id=own_account_id,
            status=status,
            note=note
        )

        if response['success']:
            return JsonResponse({"success": True, 'status': 200, "message": "쿠폰 수정 성공"})
        else:
            return JsonResponse({"success": False, 'status': 400, "message": "쿠폰 수정 실패", "errors": response['message']})
