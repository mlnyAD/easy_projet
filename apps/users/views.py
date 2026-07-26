

from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from framework.runtime import EPList, ListPage
from framework.viewmodel.builder import ListViewModelBuilder


from .lists import USER_LIST_DEFINITION
from .models import User


class UserListView(ListView):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"
    paginate_by = 20

    def get_queryset(self):
        return (
            User.objects
            .select_related(
                "company",
                "global_role",
                "access_level",
                "employment_type",
                "job",
            )
            .order_by("last_name", "first_name")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        django_page = context["page_obj"]

        runtime = EPList(
            definition=USER_LIST_DEFINITION,
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
        context["actions_template"] = "users/user_actions.html"

        return context

