from django.conf import settings

def main_url(request):
    return {
        "MAIN_URL": settings.MAIN_URL
    }
