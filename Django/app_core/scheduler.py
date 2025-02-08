from datetime import timedelta, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from . import models
import datetime

def startScheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(empty_schedule_job, 'interval', hours=2) # 2시간마다 실행
    scheduler.add_job(review_search_weight, 'interval', hours=6) # 6시간마다 실행
    scheduler.add_job(coupon_expire, 'cron', hour=0, minute=0) # 매일 0시 0분에 실행
    scheduler.add_job(place_ad_manage, 'cron', hour=0, minute=30) # 매일 0시 30분에 실행
    scheduler.add_job(delete_account, 'cron', hour=1, minute=0) # 매일 1시 0분에 실행
    scheduler.add_job(place_info_status_statictic, 'cron', hour=1, minute=30) # 매일 1시 30분에 실행
    scheduler.start()

def empty_schedule_job():
    return

# 리뷰 게시글의 검색 가중치를 조정하는 함수
def review_search_weight():

    # 모든 리뷰 게시글을 가져온다.
    review_posts = models.POST.objects.filter(
        review_post__isnull=False # review_post가 null이 아닌 경우
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

    models.SERVER_LOG.objects.create(
        content=f'[SCHEDULER] {index}개의 리뷰 게시글의 검색 가중치를 다시 계산했습니다.'
    )

# 쿠폰 만료 처리 함수
def coupon_expire():

    # 모든 활성 쿠폰을 가져온다.
    coupons = models.COUPON.objects.filter(
        status='normal'
    )
    today = datetime.datetime.now()
    for coupon in coupons:
        if coupon.expire_at < today:
            coupon.status = 'expired'
            coupon.save()
            # 만료 메시지 전송
            for account_id in coupon.own_accounts:
                models.MESSAGE.objects.create(
                    to_account=account_id,
                    sender_account='supervisor',
                    title='[알림] 쿠폰 만료 안내',
                    content=f'{coupon.name} 쿠폰의 사용 기간이 만료되었습니다.'
                )
            models.SERVER_LOG.objects.create(
                content=f'[SCHEDULER] {coupon.name} 쿠폰이 만료되었습니다. 사용자에게 쿠폰 만료 메시지를 전송했습니다.'
            )

# 광고 관리 함수
def place_ad_manage():

    # 모든 광고 중인 여행지 정보를 가져온다.
    place_infos = models.PLACE_INFO.objects.all()
    today = timezone.now()
    for place_info in place_infos:
        # 광고 종료일이 지난 경우
        if place_info.status == 'ad' and place_info.ad_end_at < today:
            place_info.status = 'normal'
            place_info.save()
            models.SERVER_LOG.objects.create(
                content=f'[SCHEDULER] {place_info.post.title} 여행지의 광고가 자동 종료되었습니다.'
            )
        # 광고 시작일이 지난 경우
        elif place_info.status == 'pending' and place_info.ad_start_at < today:
            place_info.status = 'ad'
            place_info.save()
            models.SERVER_LOG.objects.create(
                content=f'[SCHEDULER] {place_info.post.title} 여행지의 광고가 자동 시작되었습니다.'
            )

def delete_account():

    # 모든 삭제 대기 중인 사용자를 가져온다.
    accounts = models.ACCOUNT.objects.filter(
        status='deleted'
    )
    today = timezone.now()
    for account in accounts:
        # last_login이 90일 이전인 경우 삭제
        if account.last_login < today - timedelta(days=90):
            account.delete()
            models.SERVER_LOG.objects.create(
                content=f'[SCHEDULER] {account.id} 사용자 데이터가 삭제되었습니다.'
            )

def place_info_status_statictic():

    # 광고 요청 여행지 게시글 갯수
    place_ad_request = models.PLACE_INFO.objects.filter(
        status='pending'
    ).count()

    # 광고 중인 여행지 게시글 갯수
    place_on_ad = models.PLACE_INFO.objects.filter(
        status='ad'
    ).count()

    # 통계 저장
    models.STATISTIC.objects.create(
        name='place_ad_request',
        value=place_ad_request
    )
    models.STATISTIC.objects.create(
        name='place_on_ad',
        value=place_on_ad
    )
