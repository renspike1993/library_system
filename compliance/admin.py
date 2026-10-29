from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html

from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter

from administrative.models import CurriculumSubject
from .models import Report


@admin.register(Report)
class ReportAdmin(ModelAdmin):
    list_display = ("description", "report_type", "date_range", "starting_from", "view_report")
    list_filter = (
        ("report_type", ChoicesDropdownFilter),
        ("date_range", ChoicesDropdownFilter),
    )
    date_hierarchy = "starting_from"
    list_filter_submit = True

    @admin.display(description="Report")
    def view_report(self, obj):
        url = reverse("admin:compliance_report_view", args=[obj.pk])
        return format_html(
            '<a href="{}" class="inline-flex items-center gap-1 px-3 py-1 '
            'text-xs font-medium rounded bg-primary-600 text-white '
            'hover:bg-primary-700 transition">View</a>',
            url,
        )

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "<int:pk>/view/",
                self.admin_site.admin_view(self.view_report_page),
                name="compliance_report_view",
            ),
        ]
        return custom + urls

    def view_report_page(self, request, pk):
        obj = self.get_object(request, pk)
        if obj is None:
            from django.http import Http404
            raise Http404("Report not found")

        # --- Subjects with their assigned books ---
        subjects = (
            CurriculumSubject.objects
            .select_related("subject", "curriculum", "curriculum__program")
            .prefetch_related("books")
            .order_by("subject__code")
        )

        context = {
            **self.admin_site.each_context(request),
            "title": f"Report: {obj.description}",
            "obj": obj,
            "opts": self.model._meta,
            "subjects": subjects,
        }
        from django.template.response import TemplateResponse
        return TemplateResponse(
            request,
            "admin/compliance/report/blank.html",
            context,
        )