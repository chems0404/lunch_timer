from django.conf import settings


def company_settings(request):
    return {
        "COMPANY_NAME": settings.COMPANY_NAME,
        "COMPANY_LOGO_URL": settings.COMPANY_LOGO_URL,
    }