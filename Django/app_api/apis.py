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
# class api_post(APIView): 게시글 REST API
# - GET: 게시글 조회
# - DELETE: 게시글 삭제
# - PATCH: 게시글 좋아요 토글
# class api_place_info(APIView): 여행지 정보 REST API
# - PATCH: 여행지 정보 수정
# class api_account(APIView): 사용자 REST API
# - GET: 사용자 정보 검섹
# - POST: 사용자 정보 생성
# - PATCH: 사용자 정보 수정
# class api_message(APIView): 메세지 REST API
# - GET: 메세지 읽음 처리
# - POST: 메세지 발송
# class api_comment(APIView): 댓글 REST API
# - POST: 댓글 작성
# - PATCH: 댓글 수정
# - DELETE: 댓글 삭제
# class api_coupon(APIView): 쿠폰 REST API
# - GET: 쿠폰 검색
# - POST: 쿠폰 생성
# - PATCH: 쿠폰 수정
# class api_board(APIView): 게시판 REST API
# - POST: 게시판 생성
# - PATCH: 게시판 수정
# - DELETE: 게시판 삭제
# class api_category(APIView): 카테고리 REST API
# - POST: 카테고리 생성
# - PATCH: 카테고리 수정
# - DELETE: 카테고리 삭제
# class api_ip_block(APIView): IP 차단 REST API
# - POST: IP 차단
# - DELETE: IP 차단 해제



# 로그인 api
def api_login(request):

    # id, password를 받아 로그인 처리
    id = request.POST.get('id')
    password = request.POST.get('password')
    remember = request.POST.get('remember')

    # 로그인 처리
    user = authenticate(username=id, password=password)

    if user is None: # 로그인 실패
        return JsonResponse({"success": False, 'status': 400, "message": "아이디 또는 비밀번호가 일치하지 않습니다."})
    else: # 로그인 성공

        # 아이피 차단 여부 확인
        blocked_ips = daos.select_blocked_ips()
        user_ip = request.META.get('REMOTE_ADDR')
        if user_ip in blocked_ips:
            return JsonResponse({"success": False, 'status': 400, "message": "아이디 또는 비밀번호가 일치하지 않습니다."})

        # 로그인 처리
        login(request, user)

        # 사용자 활동 기록 생성
        daos.create_account_activity(
            account_id=user.id,
            message=f'[로그인] {user.username}님이 로그인하였습니다.'
        )
        daos.update_account(
            account_id=user.id,
            recent_ip=user_ip
        )

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
    file_path = daos.upload_file(file)['path']
    response = {
        'path': 'media/' + str(file_path),
    }

    return JsonResponse({"success": True, 'status': 200, "message": "파일 업로드 성공", 'data': response})

# 게시글 REST API
# GET: 게시글 조회
# DELETE: 게시글 삭제
# PATCH: 게시글 좋아요 토글
class api_post(APIView):
    # 게시글 조회 api(GET)
    def get(self, request, *args, **kwargs):

        # 게시글 조회
        post_id = request.query_params.get('post_id')
        title = request.query_params.get('title')

        post = daos.select_post(post_id, title)

        return JsonResponse({"success": True, 'status': 200, "message": "게시글 조회 성공", 'data': post})

    # 게시글 삭제 api(DELETE)
    def delete(self, request, *args, **kwargs):

        # 게시글 삭제
        post_id = request.query_params.get('post_id')

        # 로그인 여부 확인
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, 'status': 401, "message": "로그인이 필요합니다."})

        # 게시글 확인
        if 'post' not in request.user.subsupervisor_permissions:
            post = daos.select_post(post_id)
            if post['author']['id'] != request.user.id:
                return JsonResponse({"success": False, 'status': 403, "message": "권한이 없습니다."})

        # 게시글 삭제
        daos.delete_post(post_id)

        # 사용자 활동 기록 생성
        daos.create_account_activity(
            account_id=request.user.id,
            message=f'[게시글삭제] {post["title"]} 게시글이 삭제되었습니다.'
        )

        return JsonResponse({"success": True, 'status': 200, "message": "게시글 삭제 성공"})

    # 게시글 좋아요 토글 api(PATCH)
    def patch(self, request, *args, **kwargs):

        # 게시글 좋아요 토글
        post_id = request.data.get('post_id')

        # 로그인 여부 확인
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, 'status': 401, "message": "로그인이 필요합니다."})

        # 게시글 확인
        post = daos.select_post(post_id)

        # 게시글 타입 확인 후 좋아요 처리
        if post['place_info'] == None: # 세션으로 처리(기본 게시글)
            user_like_posts = request.session.get('like_post_ids', '')
            if str(post['id']) in user_like_posts:
                request.session['like_post_ids'] = user_like_posts.replace(str(post['id']) + ',', '')
                is_liked = False

                # 사용자 활동 기록 생성
                daos.create_account_activity(
                    account_id=request.user.id,
                    message=f'[좋아요] {post["title"]} 게시글에 좋아요를 취소하였습니다.'
                )
            else:
                request.session['like_post_ids'] = user_like_posts + str(post['id']) + ','
                is_liked = True

                # 사용자 활동 기록 생성
                daos.create_account_activity(
                    account_id=request.user.id,
                    message=f'[좋아요] {post["title"]} 게시글에 좋아요를 눌렀습니다.'
                )
        else: # 데이터베이스로 처리(장소 게시글)
            user_bookmark_posts = daos.select_account(request.user.id)['bookmarked_posts']
            if str(post['id']) in user_bookmark_posts:
                request.user.bookmarked_posts.remove(
                    models.POST.objects.get(id=post_id)
                )
                request.user.save()
                is_liked = False

                # 사용자 활동 기록 생성
                daos.create_account_activity(
                    account_id=request.user.id,
                    message=f'[좋아요] {post["title"]} 게시글을 즐겨찾기에서 삭제하였습니다.'
                )
            else:
                request.user.bookmarked_posts.add(
                    models.POST.objects.get(id=post_id)
                )
                request.user.save()
                is_liked = True

                # 사용자 활동 기록 생성
                daos.create_account_activity(
                    account_id=request.user.id,
                    message=f'[좋아요] {post["title"]} 게시글을 즐겨찾기에 추가하였습니다.'
                )

            # 게시글 업데이트
            if is_liked:
                like_count = int(post['like_count']) + 1
            else:
                like_count = int(post['like_count']) - 1
            daos.update_post(post_id, like_count=like_count)

        return JsonResponse({"success": True, 'status': 200, "message": "게시글 좋아요 토글 성공"})

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
            nickname=nickname,
            partner_name=partner_name,
            email=email,
            account_type=account_type,
            tel=tel
        )

        # 기본 게시글 생성
        if account_type == 'partner':
            board_ids = request.data.get('board_ids', '1')
            category_ids = request.data.get('category_ids', '1')
            address = request.data.get('address', '서울특별시 강남구 역삼동 123-456')
            post = daos.create_post(
                author_id=account['pk'],
                title='기본 여행지 게시글 제목',
                content='여행지 내용을 입력해주세요.',
                board_ids=board_ids,
            )
            place_info = daos.create_post_place_info(
                post_id=post['pk'],
                category_ids=category_ids,
                location_info='위치 안내 메세지를 입력해주세요.',
                open_info='영업 정보를 입력해주세요.',
                address=address,
                status='writing'
            )
            daos.update_post(
                post_id=post['pk'],
                place_info_id=place_info['pk']
            )

        # 기본 포인트 지급
        register_point = daos.select_server_setting('register_point')
        daos.update_account(
            account_id=account['pk'],
            mileage=register_point,
            exp=register_point
        )

        # 활동 기록 생성
        daos.create_account_activity(
            account_id=account['pk'],
            message=f'[가입] {nickname}님이 가입하였습니다.',
            exp_change=register_point,
            mileage_change=register_point
        )

        return JsonResponse({"success": True, 'status': 200, "message": "사용자 생성 성공", 'data': account['status']})

    # 사용자 수정 api(PATCH)
    def patch(self, request, *args, **kwargs):

        # 사용자 수정
        id = int(request.data.get('id', 0))

        # 계정 확인
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, 'status': 401, "message": "로그인이 필요합니다."})
        account = daos.select_account(request.user.id)
        if request.user.id != id:
            if 'user' not in account['subsupervisor_permissions']:
                return JsonResponse({"success": False, 'status': 403, "message": "권한이 없습니다."})

        # 수정할 데이터
        password = request.data.get('password')
        nickname = request.data.get('nickname')
        partner_name = request.data.get('partner_name')
        email = request.data.get('email')
        tel = request.data.get('tel')
        exp = None
        mileage = None
        status = None
        subsupervisor_permissions = None
        if 'user' in account['subsupervisor_permissions']: # 사용자 수정 권한이 있는 경우
            exp = request.data.get('exp')
            mileage = request.data.get('mileage')
            status = request.data.get('status')
        if account['account_type'] == 'supervisor': # 최상위 관리자인 경우
            subsupervisor_permissions = request.data.get('subsupervisor_permissions') # ,로 구분된 문자열(user,post,coupon,setting..)

        daos.update_account(
            account_id=id,
            password=password,
            nickname=nickname,
            partner_name=partner_name,
            email=email,
            tel=tel,
            exp=exp,
            mileage=mileage,
            status=status,
            subsupervisor_permissions=subsupervisor_permissions
        )

        # 활동 기록 생성
        profile = daos.select_account(id)
        daos.create_account_activity(
            account_id=id,
            message=f'[수정] {profile["username"]}님의 정보가 수정되었습니다.'
        )

        # 로그인 유지
        if request.user.id == id:
            user = authenticate(username=account['username'], password=password)
            login(request, user)

        return JsonResponse({"success": True, 'status': 200, "message": "사용자 수정 성공"})

    def delete(self, request, *args, **kwargs):

        # 계정 확인
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, 'status': 401, "message": "로그인이 필요합니다."})
        if 'user' in request.user.subsupervisor_permissions:
            id = request.query_params.get('id', request.user.id)
        else:
            id = request.user.id

        # 사용자 삭제
        daos.delete_account(id)

        # 활동 기록 생성
        daos.create_account_activity(
            account_id=request.user.id,
            message=f'[삭제] {id}님의 정보가 삭제되었습니다.'
        )

        return JsonResponse({"success": True, 'status': 200, "message": "사용자 삭제 성공"})

# 메세지 REST API
class api_message(APIView):
    # 메세지 읽음 처리 api(GET)
    def get(self, request, *args, **kwargs):

        # 로그인 여부 확인
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, 'status': 401, "message": "로그인이 필요합니다."})

        # 메세지 읽음 처리 및 쿠폰 수령
        message_id = request.query_params.get('message_id')
        receive_coupon = request.query_params.get('receive_coupon')

        # 쿠폰 수령 확인
        if receive_coupon == 'true':
            message = daos.select_message(message_id)
            if message['include_coupon'] == None:
                return JsonResponse({"success": False, 'status': 400, "message": "쿠폰이 포함되어있지 않습니다."})
            if request.user.mileage < message['include_coupon']['required_mileage']:
                return JsonResponse({"success": False, 'status': 400, "message": "마일리지가 부족합니다."})
            daos.update_account(account_id=request.user.id, mileage=request.user.mileage - message['include_coupon']['required_mileage'])
            daos.update_message(message_id, delete_coupon=True)
            daos.create_account_activity(
                account_id=request.user.id,
                message=f'[쿠폰수령] {message["include_coupon"]["code"]} 쿠폰을 수령하였습니다.',
                mileage_change=-message['include_coupon']['required_mileage']
            )
        else:
            daos.update_message(message_id) # 메세지 읽음 처리

        return JsonResponse({"success": True, 'status': 200, "message": "메세지 처리 성공"})

    # 메세지 생성 api(POST)
    def post(self, request, *args, **kwargs):

        # 로그인 여부 확인
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, 'status': 401, "message": "로그인이 필요합니다."})

        # 메세지 데이터
        receiver_id = request.data.get('receiver_id')
        if 'supervisor' == receiver_id:
            receiver_id = None # 관리자는 None
        sender_id = request.user.id
        if 'message' in request.user.subsupervisor_permissions:
            sender_id = None # 관리자는 None
        title = request.data.get('title')
        content = request.data.get('content')
        image = request.data.get('image')
        include_coupon_code = request.data.get('include_coupon_code')
        message_type = request.data.get('message_type')

        # 메세지 생성
        response = daos.create_message(
            sender_account_id=sender_id,
            receive_account_id=receiver_id,
            title=title,
            content=content,
            image=image,
            include_coupon_code=include_coupon_code,
            message_type=message_type
        )

        # 활동 기록 생성
        if receiver_id == None:
            receiver_id = '관리자'
        daos.create_account_activity(
            account_id=sender_id,
            message=f'[메세지] {receiver_id}님에게 메세지를 보냈습니다.'
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
        parent_comment_id = request.data.get('parent_comment_id')
        content = request.data.get('content')

        response = daos.create_comment(
            account_id=request.user.id,
            parent_comment_id=parent_comment_id,
            post_id=post_id,
            content=content
        )

        if response['success']:

            # 활동 기록 생성
            if response['type'] == 'attendance':
                daos.create_account_activity(
                    account_id=request.user.id,
                    message=f'[출석] {request.user.username}님이 출석하였습니다.',
                    exp_change=response['point'],
                    mileage_change=response['point']
                )
            elif response['type'] == 'greeting':
                daos.create_account_activity(
                    account_id=request.user.id,
                    message=f'[인사] {request.user.username}님이 가입 인사를 하였습니다.',
                    exp_change=response['point'],
                    mileage_change=response['point']
                )
            elif response['type'] == 'talk':
                daos.create_account_activity(
                    account_id=request.user.id,
                    message=f'[대화] {request.user.username}님이 대화 메세지를 남겼습니다.',
                    exp_change=response['point'],
                    mileage_change=response['point']
                )
            elif parent_comment_id == None:
                daos.create_account_activity(
                    account_id=request.user.id,
                    message=f'[댓글] {request.user.username}님이 댓글을 작성하였습니다.',
                    exp_change=response['point'],
                    mileage_change=response['point']
                )
            else:
                daos.create_account_activity(
                    account_id=request.user.id,
                    message=f'[대댓글] {request.user.username}님이 대댓글을 작성하였습니다.',
                    exp_change=response['point'],
                    mileage_change=response['point']
                )
                daos.create_account_activity(
                    account_id=response['parent_comment_author_id'],
                    message=f'[대댓글] {request.user.username}님이 댓글에 대댓글을 작성하였습니다.'
                )

            return JsonResponse({"success": True, 'status': 200, "message": "댓글 생성 성공"})
        else:
            return JsonResponse({"success": False, 'status': 400, "message": "댓글 생성 실패", "errors": response['message']})

    # 댓글 수정 api(PATCH)
    def patch(self, request, *args, **kwargs):

        # 댓글 수정
        comment_id = request.data.get('comment_id')
        content = request.data.get('content')
        hide = True if request.data.get('hide') == 'true' else False if request.data.get('hide') == 'false' else None

        # 댓글 수정
        response = daos.update_comment(
            comment_id=comment_id,
            content=content,
            hide=hide
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

        # 활동 기록 생성
        daos.create_account_activity(
            account_id=request.user.id,
            message=f'[댓글삭제] {request.user.username}님의 댓글이 삭제되었습니다.'
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
        name = request.query_params.get('name')

        response = daos.select_all_coupons(
            code=code,
            name=name
        )

        return JsonResponse({"success": True, 'status': 200, "message": "쿠폰 조회 성공", 'data': response})

    # 쿠폰 생성 api(POST)
    def post(self, request, *args, **kwargs):

        # 로그인 여부 확인
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, 'status': 401, "message": "로그인이 필요합니다."})
        create_account_id = request.user.id

        response = daos.create_coupon(
            account_id=request.user.id,
            code=request.data.get('code'),
            related_post_id=request.data.get('post_id'),
            name=request.data.get('name'),
            content=request.data.get('content'),
            image=request.data.get('image'),
            expire_at=request.data.get('expire_at'),
            required_mileage=request.data.get('required_mileage')
        )

        # 활동 기록 생성
        daos.create_account_activity(
            account_id=create_account_id,
            message=f'[쿠폰생성] {request.user.username}님이 쿠폰을 생성하였습니다.'
        )

        if response['success']:
            return JsonResponse({"success": True, 'status': 200, "message": "쿠폰 생성 성공", 'pk': response['pk']})
        else:
            return JsonResponse({"success": False, 'status': 400, "message": "쿠폰 생성 실패", "errors": response['message']})

    # 쿠폰 수정 api(PATCH)
    def patch(self, request, *args, **kwargs):

        # 쿠폰 상태 변경 여부 확인
        status = request.data.get('status')
        if status == 'used': # 사용 상태로 변경 요청 시
            coupon = daos.select_coupon(request.data.get('code'))
            own_account = daos.select_account(coupon['own_account']['id'])
            if own_account['mileage'] < coupon['required_mileage']:
                return JsonResponse({"success": False, 'status': 400, "message": "마일리지가 부족합니다."})
            else: # 사용 처리
                daos.update_account(
                    account_id=own_account['id'],
                    mileage=own_account['mileage'] - coupon['required_mileage']
                )
                daos.create_account_activity(
                    account_id=own_account['id'],
                    message=f'[쿠폰사용] {coupon["code"]} 쿠폰을 사용하였습니다.',
                    mileage_change=-coupon['required_mileage']
                )

        # 쿠폰 수정
        response = daos.update_coupon(
            code=request.data.get('code'),
            name=request.data.get('name'),
            content=request.data.get('content'),
            image=request.data.get('image'),
            expire_at=request.data.get('expire_at'),
            required_mileage=request.data.get('required_mileage'),
            own_account_id=request.data.get('own_account_id'),
            status=status,
            note=request.data.get('note'),
            related_post_id=request.data.get('post_id')
        )

        if response['success']:
            return JsonResponse({"success": True, 'status': 200, "message": "쿠폰 수정 성공"})
        else:
            return JsonResponse({"success": False, 'status': 401, "message": "쿠폰 수정 실패", "errors": response['message']})

# 게시판 REST API
class api_board(APIView):

    # 게시판 생성 api(POST)
    def post(self, request, *args, **kwargs):

        # 권한 확인
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, 'status': 401, "message": "로그인이 필요합니다."})
        if 'post' not in request.user.subsupervisor_permissions:
            return JsonResponse({"success": False, 'status': 403, "message": "권한이 없습니다."})

        # 게시판 생성
        name = request.data.get('name')
        board_type = request.data.get('board_type')
        parent_board_id = request.data.get('parent_board_id')
        display_weight = request.data.get('display_weight')
        level_cut = request.data.get('level_cut')
        display_groups = request.data.get('display_groups')
        write_groups = request.data.get('write_groups')
        comment_groups = request.data.get('comment_groups')
        daos.create_board(
            name=name,
            board_type=board_type,
            display_groups=display_groups,
            write_groups=write_groups,
            comment_groups=comment_groups,
            level_cut=level_cut,
            display_weight=display_weight,
            parent_board_id=parent_board_id
        )

        return JsonResponse({"success": True, 'status': 200, "message": "게시판 생성 성공"})

    # 게시판 수정 api(PATCH)
    def patch(self, request, *args, **kwargs):

        # 권한 확인
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, 'status': 401, "message": "로그인이 필요합니다."})
        if 'post' not in request.user.subsupervisor_permissions:
            return JsonResponse({"success": False, 'status': 403, "message": "권한이 없습니다."})

        # 게시판 수정
        board_id = request.query_params.get('board_id')
        name = request.data.get('name')
        board_type = request.data.get('board_type')
        parent_board_id = request.data.get('parent_board_id')
        display_weight = request.data.get('display_weight')
        level_cut = request.data.get('level_cut')
        display_groups = request.data.get('display_groups')
        write_groups = request.data.get('write_groups')
        comment_groups = request.data.get('comment_groups')
        daos.update_board(
            board_id=board_id,
            name=name,
            board_type=board_type,
            display_groups=display_groups,
            write_groups=write_groups,
            comment_groups=comment_groups,
            level_cut=level_cut,
            display_weight=display_weight,
            parent_board_id=parent_board_id
        )

        return JsonResponse({"success": True, 'status': 200, "message": "게시판 수정 성공"})

    # 게시판 삭제 api(DELETE)
    def delete(self, request, *args, **kwargs):

        # 권한 확인
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, 'status': 401, "message": "로그인이 필요합니다."})
        if 'post' not in request.user.subsupervisor_permissions:
            return JsonResponse({"success": False, 'status': 403, "message": "권한이 없습니다."})

        # 게시판 삭제
        board_id = request.query_params.get('board_id')
        daos.delete_board(board_id)

        return JsonResponse({"success": True, 'status': 200, "message": "게시판 삭제 성공"})

# 카테고리 REST API
class api_category(APIView):

    # 카테고리 생성 api(POST)
    def post(self, request, *args, **kwargs):

        # 권한 확인
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, 'status': 401, "message": "로그인이 필요합니다."})
        if 'ad' not in request.user.subsupervisor_permissions:
            return JsonResponse({"success": False, 'status': 403, "message": "권한이 없습니다."})

        # 카테고리 생성
        name = request.data.get('name')
        parent_category_id = request.data.get('parent_category_id')
        display_weight = request.data.get('display_weight')
        daos.create_category(
            name=name,
            display_weight=display_weight,
            parent_category_id=parent_category_id
        )

        return JsonResponse({"success": True, 'status': 200, "message": "카테고리 생성 성공"})

    # 카테고리 수정 api(PATCH)
    def patch(self, request, *args, **kwargs):

        # 권한 확인
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, 'status': 401, "message": "로그인이 필요합니다."})
        if 'post' not in request.user.subsupervisor_permissions:
            return JsonResponse({"success": False, 'status': 403, "message": "권한이 없습니다."})

        # 카테고리 수정
        category_id = request.query_params.get('category_id')
        name = request.data.get('name')
        display_weight = request.data.get('display_weight')
        daos.update_category(
            category_id=category_id,
            name=name,
            display_weight=display_weight
        )

        return JsonResponse({"success": True, 'status': 200, "message": "카테고리 수정 성공"})

    # 카테고리 삭제 api(DELETE)
    def delete(self, request, *args, **kwargs):

        # 권한 확인
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, 'status': 401, "message": "로그인이 필요합니다."})
        if 'post' not in request.user.subsupervisor_permissions:
            return JsonResponse({"success": False, 'status': 403, "message": "권한이 없습니다."})

        # 카테고리 삭제
        category_id = request.query_params.get('category_id')
        daos.delete_category(category_id)

        return JsonResponse({"success": True, 'status': 200, "message": "카테고리 삭제 성공"})



# IP 차단 REST API
class api_ip_block(APIView):

    # IP 차단 api(POST)
    def post(self, request, *args, **kwargs):

        # 권한 확인
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, 'status': 401, "message": "로그인이 필요합니다."})
        if 'user' not in request.user.subsupervisor_permissions:
            return JsonResponse({"success": False, 'status': 403, "message": "권한이 없습니다."})

        # IP 차단
        ip = request.query_params.get('ip')
        daos.create_blocked_ip(ip)

        return JsonResponse({"success": True, 'status': 200, "message": "IP 차단 성공"})

    # IP 차단 해제 api(DELETE)
    def delete(self, request, *args, **kwargs):

        # 권한 확인
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, 'status': 401, "message": "로그인이 필요합니다."})
        if 'user' not in request.user.subsupervisor_permissions:
            return JsonResponse({"success": False, 'status': 403, "message": "권한이 없습니다."})

        # IP 차단 해제
        ip = request.query_params.get('ip')
        daos.delete_blocked_ip(ip)

        return JsonResponse({"success": True, 'status': 200, "message": "IP 차단 해제 성공"})
