

from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from .forms import CompanyForm
from .models import Company

from .lists import COMPANY_LIST_DEFINITION

from framework.runtime import EPList, ListPage
from framework.viewmodel.builder import ListViewModelBuilder

class CompanyListView(ListView):
    model = Company
    template_name = "companies/company_list.html"
    context_object_name = "companies"
    paginate_by = 20
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        django_page = context["page_obj"]

        runtime = EPList(
            definition=COMPANY_LIST_DEFINITION,
            rows=django_page.object_list,
        )

        framework_page = ListPage(
            rows=tuple(django_page.object_list),
            page=django_page.number,
            page_size=django_page.paginator.per_page,
            total_items=django_page.paginator.count,
            total_pages=django_page.paginator.num_pages,
            has_previous=django_page.has_previous(),
            has_next=django_page.has_next(),
        )

        context["list"] = ListViewModelBuilder().build(
            runtime=runtime,
            page=framework_page,
        )

        context["page_sizes"] = (10, 20, 50, 100)
        
        context["actions_template"] = "companies/company_actions.html"

        return context
    
class CompanyCreateView(CreateView):
    model = Company
    form_class = CompanyForm
    template_name = "companies/company_form.html"
    success_url = reverse_lazy("companies:list")

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "La société a été créée avec succès.",
        )

        return response
    
class CompanyUpdateView(UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = "companies/company_form.html"
    success_url = reverse_lazy("companies:list")

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "La société a été modifiée avec succès.",
        )

        return response