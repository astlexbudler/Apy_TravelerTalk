from django.conf import settings

def main_url(request):
    return {
        "MAIN_URL": settings.MAIN_URL,
        'PARTNER_URL': settings.PARTNER_URL,
        'SUPERVISOR_URL': settings.SUPERVISOR_URL,
    }
