from django.conf import settings
from django.templatetags.static import static


def company_settings(request):
    logo_url = settings.COMPANY_LOGO_URL or static("img/logo.png")

    return {
        "COMPANY_NAME": settings.COMPANY_NAME,
        "COMPANY_LOGO_URL": logo_url,
    }