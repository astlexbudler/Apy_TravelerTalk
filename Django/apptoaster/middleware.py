# yourapp/middleware.py

import os
from django.http import HttpResponse

class ExpiryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.flag_file = "/tmp/django_server_disabled.flag"

    def __call__(self, request):
        if os.path.exists(self.flag_file):
            return HttpResponse(
                "관리자에 의해 사이트가 비활성화 되었습니다. 점검중이거나 서비스가 일시 중단되었습니다. 잠시 후 다시 시도해 주세요.",
                status=503
            )
        return self.get_response(request)
