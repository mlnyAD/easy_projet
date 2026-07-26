

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin


class EPLoginRequiredMixin(LoginRequiredMixin):

    def dispatch(self, request, *args, **kwargs):
        if settings.DEBUG:
            return super(LoginRequiredMixin, self).dispatch(
                request,
                *args,
                **kwargs,
            )

        return super().dispatch(request, *args, **kwargs)