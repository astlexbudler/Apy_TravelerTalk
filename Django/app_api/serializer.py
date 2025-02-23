from rest_framework import serializers
from app_core import models

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.COMMENT
        # 모델 필드에 따라 필요한 필드를 선택하세요.
        # 예시에서는 id, content, created_at, updated_at를 사용합니다.
        fields = ['id', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
