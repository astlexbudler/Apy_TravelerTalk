from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Comment
from .serializers import CommentSerializer
from django.http import JsonResponse

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

        # 응답
        accounts = [{
            'id': 'username',
            'nickname': 'first_name',
            'status': 'active'
        }]
        response = {
            'accounts': accounts,
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

        return JsonResponse({"success": True, 'status': 200, "message": "사용자 생성 성공"})

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

        return JsonResponse({"success": True, 'status': 200, "message": "사용자 수정 성공"})

# 메세지 REST API
class api_message(APIView):
    # 메세지 읽음 처리 api(GET)
    def get(self, request, *args, **kwargs):

        # 메세지 읽음 처리
        message_id = request.query_params.get('message_id')
        account_id = request.user.username

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

        return JsonResponse({"success": True, 'status': 200, "message": "메세지 생성 성공"})

# 댓글 REST API
class api_comment(APIView):
    # 댓글 생성 api(POST)
    def post(self, request, *args, **kwargs):

        # 댓글 생성
        post_id = request.data.get('post_id')
        account_id = request.user.username
        content = request.data.get('content')

        return JsonResponse({"success": True, 'status': 200, "message": "댓글 생성 성공"})

    # 댓글 수정 api(PATCH)
    def patch(self, request, *args, **kwargs):

        # 댓글 수정
        comment_id = request.data.get('comment_id')
        content = request.data.get('content')

        return JsonResponse({"success": True, 'status': 200, "message": "댓글 수정 성공"})

    # 댓글 삭제 api(DELETE)
    def delete(self, request, *args, **kwargs):

        # 댓글 삭제
        comment_id = request.query_params.get('comment_id')

        return JsonResponse({"success": True, 'status': 200, "message": "댓글 삭제 성공"})

# 쿠폰 REST API
class api_coupon(APIView):
    # 쿠폰 조회 api(GET)
    def get(self, request, *args, **kwargs):

        # 쿠폰 조회
        code = request.query_params.get('code')

        # 응답
        coupon = {
            'code': 'coupon_code',
            'title': 'coupon_title',
        }
        response = {
            'coupon': coupon,
        }

        return JsonResponse({"success": True, 'status': 200, "message": "쿠폰 조회 성공"})

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

        return JsonResponse({"success": True, 'status': 200, "message": "쿠폰 생성 성공"})

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

        return JsonResponse({"success": True, 'status': 200, "message": "쿠폰 수정 성공"})









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