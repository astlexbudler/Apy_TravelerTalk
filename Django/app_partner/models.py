from django.db import models

##########
# 모델 정의

# 파트너 카테고리 모델(트리형태)
# 최대 4단계까지 트리를 형성할 수 있음.
# 최상위 카테고리는 parent_id가 없음.
# 파트너 카테고리는 광고 게시글에 표시되며, 프로필에서 변경 가능.
# 파트너 회원가입 시 카테고리를 선택하고 가입함.
class CATEGORY(models.Model):
  id = models.AutoField(primary_key=True)
  parent_id = models.CharField(null=True, blank=True, help_text="상위 카테고리 ID(없으면 )", max_length=60)
  name = models.CharField(max_length=100, help_text="카테고리 이름(최대 100자)")
  def save(self, *args, **kwargs):
    if not self.parent_id:
      self.parent_id = ''
    super(CATEGORY, self).save(*args, **kwargs)