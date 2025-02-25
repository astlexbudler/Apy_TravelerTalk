from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from app_core import models, daos
from . import serializer as serializers
from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import get_object_or_404
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

    return JsonResponse({"success": True, 'status': 200, "message": "로그인 성공"})

# 로그아웃 api
def api_logout(request):

    # 로그아웃 처리
    # logout(request)

    return JsonResponse({"success": True, 'status': 200, "message": "로그아웃 성공"})

# 파일 업로드 api
def api_file_upload(request):

    # 파일 업로드 처리
    file = request.FILES['file']

    # 응답
    file_path = ''
    response = {
        'path': 'media/' + file_path,
    }

    return JsonResponse({"success": True, 'status': 200, "message": "파일 업로드 성공"})

# 쿠폰 받기 api
def api_receive_coupon(request):

    # 메세지 아이디 확인
    message_id = request.POST.get('message_id')
    account_id = request.user.username

    return JsonResponse({"success": True, 'status': 200, "message": "쿠폰 받기 성공"})

# 게시글 좋아요 토글 api
def api_like_post(request):

    # 게시글 아이디 확인
    post_id = request.POST.get('post_id')
    account_id = request.user.username
    account_like_post_ids = request.session.get('like_post_ids', '')

    # 응답
    response = {
        'is_liked': False,
    }

    return JsonResponse({"success": True, 'status': 200, "message": "게시글 좋아요 토글 성공"})

# 사용자 REST API
class api_account(APIView):
    # 사용자 검색 api(GET)
    def get(self, request, *args, **kwargs):

        # 사용자 검색
        id = request.query_params.get('id')
        nickname = request.query_params.get('nickname')
        any = request.query_params.get('any') # 닉네임 또는 아이디로 검색

        # 필터 조건 설정
        filters = Q()

        if any:
            # 'username' 또는 'first_name' 필드에서 'any' 값이 포함된 사용자 찾기
            filters &= (Q(username__icontains=any) | Q(first_name__icontains=any))

        if id:
            filters &= Q(username__icontains=id)
        if nickname:
            filters &= Q(first_name__icontains=nickname)

        # 필터된 사용자 목록 가져오기
        accounts = models.ACCOUNT.objects.filter(filters)

        # 시리얼라이저를 사용해 반환할 데이터 생성
        serializer = serializers.AccountSerializer(accounts, many=True)

        response = {
            'accounts': serializer.data,
            'total_count': len(accounts),
        }

        return JsonResponse({"success": True, 'status': 200, "message": "사용자 조회 성공", 'data': response})

    # 사용자 생성 api(POST)
    def post(self, request, *args, **kwargs):

        # 사용자 생성
        id = request.data.get('id')
        password = request.data.get('password')
        nickname = request.data.get('nickname')
        partner_name = request.data.get('partner_name')
        email = request.data.get('email')
        account_type = request.data.get('account_type')
        status = None
        point = None
        level = models.LEVEL_RULE.objects.get(level=1).level

        # 회원 상태 설정
        if account_type == 'partner' or account_type == 'dame': # 파트너 또는 여성 회원일 경우
            status = 'pending'
            # 승인 대기는 관리자가 확인 후 활성화 가능.
            # 승인 대기 상태에서는 일부 기능 제한
            # 글 작성, 댓글 작성, 출석 불가
        else:
            status = 'active'

        # 가입 포인트 설정
        if account_type == 'user' or account_type == 'dame': # 사용자 또는 여성 회원일 경우
            point = int(models.SERVER_SETTING.objects.get(name='register_point').value) # 가입 포인트 지급
        else:
            point = 0

        # 아이디, 닉네임 중복 확인
        if models.ACCOUNT.objects.filter(username=id).exists() or models.ACCOUNT.objects.filter(first_name=nickname).exists():
            return JsonResponse({"success": False, 'status': 400, "message": "이미 존재하는 ID 또는 닉네임 입니다."})

        # 회원가입 데이터 생성
        account_data = {
            'username': id,
            'first_name': nickname,
            'last_name': partner_name,
            'email': email,
            'status': status,
            'mileage': point,
            'exp': point,
            'level': level
        }

        # Serializer로 회원가입 처리
        serializer = serializers.AccountCreateSerializer(data=account_data)

        if serializer.is_valid():
            # 유효성 검사를 통과하면 데이터 저장
            account = serializer.save()

            account.set_password(password) # 비밀번호 설정

            if account_type == 'partner':
                account.groups.add(models.Group.objects.get(name='partner'))
            elif account_type == 'dame':
                account.groups.add(models.Group.objects.get(name='dame'))
            elif account_type == 'user':
                account.groups.add(models.Group.objects.get(name='user'))
            account.save()

            if account_type == 'partner':
                # 여행지 게시글 생성
                post = models.POST(
                    author=account, # 작성자
                    title=account.last_name + ' 여행지', # 제목
                    content='파트너사 ' + account.last_name + '의 여행지 정보입니다.', # 내용
                )
                post.save()

            # 회원가입 활동기록 생성
            if account_type == 'partner':
                models.ACTIVITY.objects.create(
                    account=account,
                    message = f'[계정] {nickname}님의 파트너사 계정을 생성했습니다.',
                )
            elif account_type == 'dame' or account_type == 'user':
                models.ACTIVITY.objects.create(
                    account=account,
                    message = f'[계정] {nickname}님의 계정을 생성했습니다.',
                    mileage_change = '+' + str(point),
                    exp_change = '+' + str(point),
                )

            # 레벨업
            daos.check_level_up(account.username)

            return JsonResponse({"success": True, 'status': 200, "message": "사용자 생성 성공"})
        else:
            # 유효하지 않은 데이터 처리
            return JsonResponse({"success": False, 'status': 400, "message": serializer.errors})

    # 사용자 수정 api(PATCH)
    def patch(self, request, *args, **kwargs):

        # 사용자 수정
        id = request.data.get('id')
        password = request.data.get('password')
        nickname = request.data.get('nickname')
        partner_name = request.data.get('partner_name')
        email = request.data.get('email')
        status = request.data.get('status')
        exp = request.data.get('exp')
        mileage = request.data.get('mileage')
        subsupervisor_permissions = request.data.get('subsupervisor_permissions') # ,로 구분된 문자열(user,post,coupon,setting..)

        # if not request.user.is_authenticated: # 비로그인 상태인 경우, 에러 반환
        #     return JsonResponse({"success": False, 'status': 401, "message": "로그인이 필요합니다."})

        # 사용자 존재 여부 확인
        try:
            account = models.ACCOUNT.objects.get(username=id)
        except account.DoesNotExist:
            return JsonResponse({"success": False, 'status': 404, "message": "사용자를 찾을 수 없습니다."})

        # 회원가입 데이터 생성
        account_data = {
            'username': id,
            'first_name': nickname,
            'last_name': partner_name,
            'email': email,
            'status': status,
            'mileage': mileage,
            'exp': exp,
            'subsupervisor_permissions': subsupervisor_permissions
        }

        # Serializer를 사용하여 데이터 검증
        serializer = serializers.AccountUpdateSerializer(account, data=account_data, partial=True)

        if serializer.is_valid():
            # 유효한 데이터라면 저장
            account = serializer.save()

            if password != '':
                account.set_password(password) # 비밀번호 설정
                account.save()

            # 레벨업
            daos.check_level_up(account.username)

            return JsonResponse({"success": True, 'status': 200, "message": "사용자 수정 성공"})
        else:
            # 유효하지 않은 데이터 처리
            return JsonResponse({"success": False, 'status': 400, "message": serializer.errors})

# 메세지 REST API
class api_message(APIView):
    # 메세지 읽음 처리 api(GET)
    def get(self, request, *args, **kwargs):

        # 메세지 읽음 처리
        message_id = request.query_params.get('message_id')

        # 메세지 조회
        try:
            message = models.MESSAGE.objects.get(id=message_id)
        except message.DoesNotExist:
            return JsonResponse({"success": False, 'status': 200, "message": "메세지가 없습니다."})

        # 읽음 처리
        message.is_read = True
        message.save()

        return JsonResponse({"success": True, 'status': 200, "message": "메세지 읽음 처리 성공"})

    # 메세지 생성 api(POST)
    def post(self, request, *args, **kwargs):

        # 메세지 생성
        sender_id = request.data.get('sender_id')
        receiver_id = request.data.get('receiver_id')
        title = request.data.get('title')
        content = request.data.get('content') # toastful editor 사용
        image = request.data.get('image')
        include_coupon_code = request.data.get('include_coupon_code')
        account_type = None

        # 발신자 계정 가져오기
        sender = models.ACCOUNT.objects.get(username=sender_id)
        if not sender:
            # 발신자가 존재하지 않으면, guest ID로 처리
            account_type = 'guest'
        else:
            # 발신자 계정이 존재하는 경우, 그에 맞는 그룹 확인 및 타입 설정
            sender_groups = [group.name for group in sender.groups.all()]
            account_type = 'user'
            if 'dame' in sender_groups:
                account_type = 'dame'
            elif 'partner' in sender_groups:
                account_type = 'partner'
            elif 'subsupervisor' in sender_groups:
                account_type = 'subsupervisor'
            elif 'supervisor' in sender_groups:
                account_type = 'supervisor'

        # 발신자 아이디 설정
        if account_type == 'guest':
            sender_id = request.session.get('guest_id', ''.join(random.choices(string.ascii_letters + string.digits, k=16)))
            request.session['guest_id'] = sender_id
        elif account_type == 'supervisor' or account_type == 'subsupervisor':
            sender_id = 'supervisor'
        else:
            sender_id = sender.username

        # 쪽지 확인
        if not title or not content: # 제목 또는 내용이 없는 경우, 에러 반환
            return JsonResponse({"success": False, 'status': 400, "message": "메세지 생성 실패", "errors": "title 또는 content가 비어있습니다."})

        # 쪽지 저장
        message_data = {
            'sender': 'supervisor' if account_type == 'supervisor' or account_type == 'subsupervisor' else sender_id,
            'to_account': receiver_id,
            'title': title,
            'content': content,
            'image': image,
        }

        if include_coupon_code: # 쿠폰 코드가 있는 경우, 쿠폰 저장
            coupon = models.COUPON.objects.filter(code=include_coupon_code).first()
            if coupon:
                message_data.include_coupon = coupon

        # Serializer로 데이터 유효성 검사 및 저장
        serializer = serializers.MessageSerializer(data=message_data)

        if serializer.is_valid():
            serializer.save()  # 데이터베이스에 저장

            # 쪽지 발송 활동기록 생성
            if request.user.is_authenticated: # 로그인 상태인 경우

                # 관리자에게 보낸 경우, receiver를 '관리자'로 설정
                if receiver_id == 'supervisor':
                    receiver = '관리자'
                else:
                    receiver = daos.get_user_profile_by_id(receiver_id).nickname

                activity = models.ACTIVITY(
                    account=request.user,
                    message = f'[쪽지] {receiver}님에게 쪽지를 보냈습니다.',
                )
                activity.save()

            return JsonResponse({"success": True, 'status': 200, "message": "메세지 생성 성공"})
        else:
            return JsonResponse({"success": False, 'status': 400, "message": "메세지 생성 실패", "errors": serializer.errors})

# 댓글 REST API
class api_comment(APIView):
    # 댓글 생성 api(POST)
    def post(self, request, *args, **kwargs):

        # 댓글 생성
        post_id = request.data.get('post_id')
        account_id = request.data.get('username')
        # account_id = request.user.username
        content = request.data.get('content')

        # 관련된 포스트와 계정 가져오기
        post = models.POST.objects.get(id=post_id)
        author = models.ACCOUNT.objects.get(username=account_id)

        # 댓글 데이터 준비
        comment_data = {
            'post': post.id,
            'author': author.id,
            'content': content
        }

        # Serializer로 데이터 유효성 검사 및 저장
        serializer = serializers.CommentSerializer(data=comment_data)

        if serializer.is_valid():
            serializer.save()  # 데이터베이스에 저장
            return JsonResponse({"success": True, 'status': 200, "message": "댓글 생성 성공"})
        else:
            return JsonResponse({"success": False, 'status': 400, "message": "댓글 생성 실패", "errors": serializer.errors})

    # 댓글 수정 api(PATCH)
    def patch(self, request, *args, **kwargs):

        # 댓글 수정
        comment_id = request.data.get('comment_id')
        content = request.data.get('content')

        # 댓글 가져오기
        comment = get_object_or_404(models.COMMENT, id=comment_id)

        # 수정할 데이터 준비
        update_data = {
            'content': content
        }

        # Serializer로 데이터 유효성 검사 및 수정
        serializer = serializers.CommentSerializer(comment, data=update_data, partial=True)

        if serializer.is_valid():
            serializer.save()  # 수정된 데이터 저장
            return JsonResponse({"success": True, 'status': 200, "message": "댓글 수정 성공"})
        else:
            return JsonResponse({"success": False, 'status': 400, "message": "댓글 수정 실패", "errors": serializer.errors})

    # 댓글 삭제 api(DELETE)
    def delete(self, request, *args, **kwargs):

        # 댓글 삭제
        comment_id = request.query_params.get('comment_id')

        # 댓글 가져오기
        comment = get_object_or_404(models.COMMENT, id=comment_id)

        # 댓글 삭제
        comment.delete()

        return JsonResponse({"success": True, 'status': 200, "message": "댓글 삭제 성공"})

# 쿠폰 REST API
class api_coupon(APIView):
    # 쿠폰 조회 api(GET)
    def get(self, request, *args, **kwargs):

        # 쿠폰 조회
        code = request.query_params.get('code')
        if not code:
            return JsonResponse({"success": False, "status": 400, "message": "쿠폰 코드가 필요합니다."})

        try:
            coupon = models.COUPON.objects.get(code=code)
        except coupon.DoesNotExist:
            return JsonResponse({"success": False, "status": 404, "message": "쿠폰을 찾을 수 없습니다."})

        # serializer로 쿠폰 객체 직렬화
        serializer = serializers.CouponSerializer(coupon)

        return JsonResponse({"success": True, "status": 200, "message": "쿠폰 조회 성공", "coupon": serializer.data})

    # 쿠폰 생성 api(POST)
    def post(self, request, *args, **kwargs):

        # 쿠폰 생성
        code = request.data.get('code')
        related_post_id = request.data.get('related_post_id')
        title = request.data.get('title')
        content = request.data.get('content') # toastful editor 사용
        image = request.data.get('image')
        expire_date = request.data.get('expire_date')
        required_mileage = request.data.get('required_mileage')
        username = request.data.get('username')

        if not all([code, title, content, expire_date, required_mileage]):
            return JsonResponse({"success": False, "status": 400, "message": "필수 항목이 누락되었습니다."})

        if models.COUPON.objects.filter(code=code).exists():
            return JsonResponse({"success": False, "status": 400, "message": "이미 존재하는 쿠폰 코드 입니다."})

        # 관련 게시글 확인
        related_post = None
        if related_post_id:
            try:
                related_post = models.POST.objects.get(id=related_post_id)
            except related_post.DoesNotExist:
                return JsonResponse({"success": False, "status": 404, "message": "게시글을 찾을 수 없습니다."})

        account = None
        if username:
            try:
                account = models.ACCOUNT.objects.get(username=username)
            except account.DoesNotExist:
                return JsonResponse({"success": False, "status": 404, "message": "사용자를 찾을 수 없습니다."})

        # 쿠폰 생성
        coupon_data = {
            'code': code,
            'name': title,
            'content': content,
            'expire_at': expire_date,
            'required_mileage': required_mileage,
            'related_post': related_post.id,
            'image': image,
            'create_account': account.id
        }

        # Serializer로 데이터 유효성 검사 및 저장
        serializer = serializers.CouponCreateSerializer(data=coupon_data)

        if serializer.is_valid():
            serializer.save()

            # 통계 데이터 생성
            coupon_create = models.STATISTIC.objects.filter(
                name='coupon_create',
                date=datetime.datetime.now().strftime('%Y-%m-%d')
            ).first()
            if coupon_create:
                coupon_create.value += 1
                coupon_create.save()
            else:
                models.STATISTIC.objects.create(
                    name='coupon_create',
                    value=1
                )

            return JsonResponse({"success": True, 'status': 200, "message": "쿠폰 생성 성공"})
        else:
            return JsonResponse({"success": False, 'status': 400, "message": "쿠폰 생성 실패", "errors": serializer.errors})


    # 쿠폰 수정 api(PATCH)
    def patch(self, request, *args, **kwargs):

        # 쿠폰 수정
        code = request.data.get('code')
        title = request.data.get('title')
        content = request.data.get('content') # toastful editor 사용
        image = request.data.get('image')
        expire_date = request.data.get('expire_date')
        required_mileage = request.data.get('required_mileage')
        own_account_id = request.data.get('own_account_id')
        status = request.data.get('status')

        if not code:
            return JsonResponse({"success": False, "status": 400, "message": "쿠폰 코드가 필요합니다."})

        # 쿠폰 조회
        try:
            coupon = models.COUPON.objects.get(code=code)
        except coupon.DoesNotExist:
            return JsonResponse({"success": False, "status": 404, "message": "쿠폰을 찾을 수 없습니다."})

        coupon_data = {
            'code': code,
            'name': title,
            'content': content,
            'expire_at': expire_date,
            'required_mileage': required_mileage,
            'own_account_id': own_account_id,
            'image': image,
            'status': status
        }

        # serializer로 업데이트
        serializer = serializers.CouponUpdateSerializer(coupon, data=coupon_data, partial=True)
        if serializer.is_valid():
            # 변경사항 저장
            serializer.save()
            return JsonResponse({"success": True, "status": 200, "message": "쿠폰 수정 성공"})
        else:
            return JsonResponse({"success": False, "status": 400, "message": serializer.errors})









'''
아래 코드 참고(이 프로젝트의 API가 아니라 그냥 예시임. 바로 사용 X)
class CommentAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # query parameter로 comment_id가 전달된 경우, 해당 댓글 조회
        comment_id = request.query_params.get('comment_id')
        if comment_id:
            try:
                comment = Comment.objects.get(pk=comment_id)
                serializer = CommentSerializer(comment)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Comment.DoesNotExist:
                return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
        # comment_id가 없는 경우 모든 댓글을 반환하거나 적절히 처리
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        # 새 댓글 생성: request.data로 전달된 데이터를 기반으로 새 댓글 생성
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # 필요에 따라 추가 로직 삽입 가능
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        # 댓글 수정: query parameter로 전달된 comment_id로 수정할 댓글 조회 후 부분 업데이트
        comment_id = request.query_params.get('comment_id')
        if not comment_id:
            return Response({"error": "Comment ID is required for update."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # partial=True로 전달된 필드만 업데이트
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # 업데이트 저장
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        # 댓글 삭제: query parameter로 전달된 comment_id로 삭제
        comment_id = request.query_params.get('comment_id')
        if not comment_id:
            return Response({"error": "Comment ID is required for delete."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            comment = Comment.objects.get(pk=comment_id)
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
'''
