

from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CompanyForm
from .models import Company


class CompanyCreateView(CreateView):
    model = Company
    form_class = CompanyForm
    template_name = "companies/company_form.html"
    success_url = reverse_lazy("companies:create")

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "La société a été créée avec succès.",
        )

        return response