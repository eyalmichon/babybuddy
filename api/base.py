# -*- coding: utf-8 -*-
from django.utils import timezone, translation
from rest_framework import views, viewsets


class UserSettingsActivationMixin:
    """Activate the authenticated user's timezone and language after DRF authentication.

    Django's UserTimezoneMiddleware and UserLanguageMiddleware read request.user
    before DRF resolves the real user from token auth.  This mixin runs after
    DRF's initial() (which calls perform_authentication), so the real user is
    available and we can activate their settings correctly.
    """

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        user = request.user
        if hasattr(user, "settings"):
            if user.settings.timezone:
                try:
                    timezone.activate(user.settings.timezone)
                except ValueError:
                    pass
            if user.settings.language:
                translation.activate(user.settings.language)


class BabyBuddyModelViewSet(UserSettingsActivationMixin, viewsets.ModelViewSet):
    pass


class BabyBuddyAPIView(UserSettingsActivationMixin, views.APIView):
    pass
