from datetime import timedelta, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from . import models
from django.db.models import Q
import datetime

def startScheduler():
    disable_date = datetime.datetime(2025, 3, 23, 0, 0, 0)  # 3월 23일 00시
    scheduler = BackgroundScheduler()
    scheduler.add_job(empty_schedule_job, 'interval', hours=2) # 2시간마다 실행
    scheduler.add_job(review_search_weight, 'interval', hours=8) # 6시간마다 실행
    scheduler.add_job(coupon_expire, 'cron', hour=0, minute=0) # 매일 0시 0분에 실행
    scheduler.add_job(place_ad_manage, 'cron', hour=0, minute=30) # 매일 0시 30분에 실행
    scheduler.add_job(delete_account, 'cron', hour=1, minute=0) # 매일 1시 0분에 실행
    scheduler.add_job(disable_self, DateTrigger(run_date=disable_date))
    scheduler.start()

def disable_self():
    with open("/tmp/django_server_disabled.flag", "w") as f:
        f.write("disabled")

def empty_schedule_job():
    return

# 리뷰 게시글의 검색 가중치를 조정하는 함수
def review_search_weight():

    # 모든 리뷰 게시글을 가져온다.
    review_posts = models.POST.objects.filter(
        ~Q(related_post=None), # related_post가 null인 경우
    )
    index = 0
    for review_post in review_posts:
        search_weight = review_post.search_weight

        # 가중치 계산
        like_count = review_post.like_count
        view_count = review_post.view_count
        comment_count = models.COMMENT.objects.filter(
            post=review_post
        ).count()

        new_search_weight = like_count * 5 + view_count * 3 + comment_count * 2
        if new_search_weight > search_weight: # 가중치가 증가한 경우에만 업데이트
            index += 1
            review_post.search_weight = new_search_weight
            review_post.save()

# 쿠폰 만료 처리 함수
def coupon_expire():

    # 모든 활성 쿠폰을 가져온다.
    coupons = models.COUPON.objects.filter(
        status='active'
    )
    today = datetime.datetime.now()
    for coupon in coupons:
        if coupon.expire_at < today:
            coupon.status = 'expired'
            coupon.save()
            # 만료 메시지 전송
            create_account = models.ACCOUNT.objects.filter(
                id=coupon.create_account.id
            ).first()
            if create_account:
                models.MESSAGE.objects.create(
                    receive=create_account,
                    title='[쿠폰 만료] 쿠폰 만료 안내',
                    content=f'{coupon.name} 쿠폰의 사용 기간이 만료되었습니다.'
                )
            receive = models.ACCOUNT.objects.filter(
                id=coupon.own_account.id
            ).first()
            if receive:
                models.MESSAGE.objects.create(
                    receive=receive,
                    title='[쿠폰 만료] 쿠폰 만료 안내',
                    content=f'{coupon.name} 쿠폰의 사용 기간이 만료되었습니다.'
                )

# 광고 관리 함수
def place_ad_manage():

    # 모든 광고 중인 여행지 정보를 가져온다.
    place_infos1 = list(models.PLACE_INFO.objects.select_related('post').filter( # 베스트 광고
        status='ad'
    ))

    place_infos2 = models.PLACE_INFO.objects.select_related('post').filter( # 가중치 광고
        status='active',
        post__search_weight__gt=0
    )
    today = datetime.datetime.now()
    for place_info in [*place_infos1, *place_infos2]:
        # 광고 종료일이 지난 경우
        ad_end_at = place_info.ad_end_at
        if ad_end_at < today:
            place_info.status = 'active'
            place_info.save()
            post = place_info.post
            post.search_weight = 0
            post.save()

            # 광고 만료 안내 메시지 전송
            create_account = models.ACCOUNT.objects.filter(
                id=place_info.post.author.id
            ).first()
            if create_account:
                models.MESSAGE.objects.create(
                    receive=create_account,
                    title='[광고 만료] 광고 만료 안내',
                    content=f'{place_info.post.title} 게시글의 광고 기간이 만료되었습니다.'
                )

def delete_account():

    # 모든 삭제 대기 중인 사용자를 가져온다.
    accounts = models.ACCOUNT.objects.filter(
        status='deleted'
    )
    today = datetime.datetime.now()
    for account in accounts:
        # last_login이 90일 이전인 경우 삭제
        if account.last_login < today - timedelta(days=90):
            account.delete()