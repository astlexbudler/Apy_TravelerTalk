from rest_framework import serializers
from app_core import models

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.COMMENT
        # 모델 필드에 따라 필요한 필드를 선택하세요.
        # 예시에서는 id, content, created_at, updated_at를 사용합니다.
        fields = ['id', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

# 계정 조회 serializer
class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ACCOUNT
        fields = ['username', 'first_name', 'status']

# 계정 생성 serializer
class AccountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ACCOUNT
        fields = ['username', 'first_name', 'last_name', 'email', 'status', 'mileage', 'exp', 'level']
        extra_kwargs = {'email': {'required': False, 'allow_null': True}}

# 계정 수정 serializer
class AccountUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ACCOUNT
        fields = ['username', 'first_name', 'last_name', 'email', 'status', 'mileage', 'exp', 'subsupervisor_permissions']
        read_only_fields = ['username']

# 메세지 생성 serializer
class MessageSerializer(serializers.ModelSerializer):
    include_coupon = serializers.PrimaryKeyRelatedField(queryset=models.COUPON.objects.all(), required=False)
    sender_account = serializers.CharField(read_only=True)  # 보낸 사람
    to_account = serializers.CharField(required=True)  # 받는 사람

    class Meta:
        model = models.MESSAGE
        fields = ['id', 'to_account', 'sender_account', 'include_coupon', 'title', 'image', 'content', 'is_read', 'created_at']
        read_only_fields = ['id', 'is_read', 'created_at']  # id, is_read, created_at은 자동 생성되므로 읽기 전용


# 댓글 생성, 수정 serializer
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.COMMENT
        fields = ['id', 'post', 'author', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']  # id와 created_at은 자동 생성되므로 읽기 전용

# 쿠폰 조회 serializer
class CouponSerializer(serializers.ModelSerializer):
    related_post = serializers.PrimaryKeyRelatedField(queryset=models.POST.objects.all(), required=False)  # 게시글 연결
    create_account = serializers.PrimaryKeyRelatedField(queryset=models.ACCOUNT.objects.all())  # 생성자
    own_account = serializers.PrimaryKeyRelatedField(queryset=models.ACCOUNT.objects.all(), required=False)  # 소유 계정

    class Meta:
        model = models.COUPON
        fields = [
            'code', 'related_post', 'create_account', 'own_account', 'name', 'image', 'content',
            'required_mileage', 'expire_at', 'created_at', 'status', 'note'
        ]
        read_only_fields = ['code', 'create_account', 'created_at']  # 읽기 전용 필드

# 쿠폰 생성 serializer
class CouponCreateSerializer(serializers.ModelSerializer):
    related_post = serializers.PrimaryKeyRelatedField(queryset=models.POST.objects.all())  # 게시글 연결
    create_account = serializers.PrimaryKeyRelatedField(queryset=models.ACCOUNT.objects.all())  # 생성자

    class Meta:
        model = models.COUPON
        fields = ['code', 'related_post', 'name', 'image', 'content', 'required_mileage', 'expire_at', 'create_account']
        read_only_fields = ['created_at']  # 읽기 전용 필드

# 쿠폰 수정 serializer
class CouponUpdateSerializer(serializers.ModelSerializer):
    related_post = serializers.PrimaryKeyRelatedField(queryset=models.POST.objects.all())  # 게시글 연결
    own_account = serializers.PrimaryKeyRelatedField(queryset=models.ACCOUNT.objects.all())  # 소유 계정

    class Meta:
        model = models.COUPON
        fields = ['code', 'related_post', 'name', 'image', 'content', 'required_mileage', 'expire_at', 'own_account', 'status']
        read_only_fields = ['code', 'created_at']  # 읽기 전용 필드
