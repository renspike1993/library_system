from django.contrib import admin
from django.db.models import Count
from django.urls import path, reverse
from django.utils.html import format_html
from django.template.response import TemplateResponse
from django.http import Http404

# Import/Export Imports
from unfold.contrib.import_export.forms import ImportForm, ExportForm
from import_export.admin import ImportExportModelAdmin

from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import (
    ChoicesDropdownFilter,
    RelatedDropdownFilter,
)

from .models import (
    Department,
    Program,
    Curriculum,
    Subject,
    CurriculumSubject,
)


# ============================================================
# Department
# ============================================================
@admin.register(Department)
class DepartmentAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm

    list_display = (
        "id",
        "abbreviation",
        "description",
        "view_books",
        "view_students",
    )
    search_fields = ("abbreviation", "description")
    list_filter_submit = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            _book_count=Count("programs__books", distinct=True),
            _student_count=Count("students", distinct=True),
        )

    @admin.display(description="Books", ordering="_book_count")
    def view_books(self, obj):
        url = (
            reverse("admin:book_book_changelist")
            + f"?program__department__id__exact={obj.pk}"
        )
        return format_html(
            '<a href="{}" class="inline-flex items-center gap-1.5 px-3 py-1 '
            'text-xs font-medium rounded bg-primary-600 text-white '
            'hover:bg-primary-700 transition">'
            '<span>View Books</span>'
            '<span class="inline-flex items-center justify-center min-w-[1.5rem] '
            'px-1.5 py-0.5 rounded-full bg-white text-primary-700 '
            'text-[11px] font-bold leading-none">{}</span>'
            "</a>",
            url,
            obj._book_count,
        )

    @admin.display(description="Students", ordering="_student_count")
    def view_students(self, obj):
        url = (
            reverse("admin:students_student_changelist")
            + f"?department__id__exact={obj.pk}"
        )
        return format_html(
            '<a href="{}" class="inline-flex items-center gap-1.5 px-3 py-1 '
            'text-xs font-medium rounded bg-green-600 text-white '
            'hover:bg-green-700 transition">'
            '<span>View Students</span>'
            '<span class="inline-flex items-center justify-center min-w-[1.5rem] '
            'px-1.5 py-0.5 rounded-full bg-white text-green-700 '
            'text-[11px] font-bold leading-none">{}</span>'
            "</a>",
            url,
            obj._student_count,
        )


# ============================================================
# Program
# ============================================================
@admin.register(Program)
class ProgramAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm

    list_display = (
        "abbreviation",
        "department",
        "description",
        "view_books",
        "view_students",
    )
    list_filter = (("department", RelatedDropdownFilter),)
    list_filter_submit = True
    search_fields = ("description", "abbreviation")
    autocomplete_fields = ("department",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_book_count=Count("books", distinct=True))

    @admin.display(description="Books", ordering="_book_count")
    def view_books(self, obj):
        url = reverse("admin:book_book_changelist") + f"?program__id__exact={obj.pk}"
        return format_html(
            '<a href="{}" class="inline-flex items-center gap-1.5 px-3 py-1 '
            'text-xs font-medium rounded bg-primary-600 text-white '
            'hover:bg-primary-700 transition">'
            '<span>View Books</span>'
            '<span class="inline-flex items-center justify-center min-w-[1.5rem] '
            'px-1.5 py-0.5 rounded-full bg-white text-primary-700 '
            'text-[11px] font-bold leading-none">{}</span>'
            "</a>",
            url,
            obj._book_count,
        )

    @admin.display(description="Students")
    def view_students(self, obj):
        url = (
            reverse("admin:students_student_changelist")
            + f"?department__id__exact={obj.department_id}"
        )
        return format_html(
            '<a href="{}" class="inline-flex items-center gap-1.5 px-3 py-1 '
            'text-xs font-medium rounded bg-green-600 text-white '
            'hover:bg-green-700 transition">'
            "<span>View Students</span>"
            "</a>",
            url,
        )


# ============================================================
# Curriculum — inline CurriculumSubject
# ============================================================
class CurriculumSubjectInline(TabularInline):
    model = CurriculumSubject
    extra = 0
    autocomplete_fields = ("subject",)
    fields = ("subject", "year_level", "semester", "category")


@admin.register(Curriculum)
class CurriculumAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm

    list_display = (
        "name",
        "program",
        "effective_year",
        "subject_count",
        "view_subjects",
        "view_books_report",
    )
    list_filter = (("program", RelatedDropdownFilter),)
    list_filter_submit = True
    search_fields = (
        "name",
        "effective_year",
        "program__abbreviation",
        "program__description",
    )
    autocomplete_fields = ("program",)
    inlines = [CurriculumSubjectInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_subject_count=Count("subjects", distinct=True))

    @admin.display(description="Subjects", ordering="_subject_count")
    def subject_count(self, obj):
        return obj._subject_count

    @admin.display(description="Subjects")
    def view_subjects(self, obj):
        url = (
            reverse("admin:administrative_curriculumsubject_changelist")
            + f"?curriculum__id__exact={obj.pk}"
        )
        return format_html(
            '<a href="{}" class="inline-flex items-center gap-1.5 px-3 py-1 '
            'text-xs font-medium rounded bg-primary-600 text-white '
            'hover:bg-primary-700 transition">'
            '<span>View Subjects</span>'
            '<span class="inline-flex items-center justify-center min-w-[1.5rem] '
            'px-1.5 py-0.5 rounded-full bg-white text-primary-700 '
            'text-[11px] font-bold leading-none">{}</span>'
            "</a>",
            url,
            obj._subject_count,
        )

    # =========================================================
    # View Books Report
    # =========================================================
    @admin.display(description="Books Report")
    def view_books_report(self, obj):
        url = reverse("admin:administrative_curriculum_books_report", args=[obj.pk])
        return format_html(
            '<a href="{}" class="inline-flex items-center gap-1.5 px-3 py-1 '
            'text-xs font-medium rounded bg-green-600 text-white '
            'hover:bg-green-700 transition" target="_blank">'
            '<span>View Books</span>'
            "</a>",
            url,
        )

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "<int:pk>/books-report/",
                self.admin_site.admin_view(self.view_books_report_page),
                name="administrative_curriculum_books_report",
            ),
        ]
        return custom + urls

    def view_books_report_page(self, request, pk):
        obj = self.get_object(request, pk)
        if obj is None:
            raise Http404("Curriculum not found")

        # Fetch subjects specifically for this curriculum, with books prefetched
        subjects = (
            CurriculumSubject.objects
            .filter(curriculum=obj)
            .select_related("subject", "curriculum", "curriculum__program")
            .prefetch_related("books")
            .order_by("year_level", "semester", "subject__code")
        )

        context = {
            **self.admin_site.each_context(request),
            "title": f"Book Holdings: {obj.name}",
            "obj": obj,
            "opts": self.model._meta,
            "subjects": subjects,
        }
        return TemplateResponse(
            request,
            "admin/curriculum/blank.html",
            context,
        )


# ============================================================
# Subject
# ============================================================
@admin.register(Subject)
class SubjectAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm

    list_display = ("code", "title", "units", "curriculum_count")
    search_fields = ("code", "title")
    list_filter_submit = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_curriculum_count=Count("curricula", distinct=True))

    @admin.display(description="Curricula", ordering="_curriculum_count")
    def curriculum_count(self, obj):
        return obj._curriculum_count


# ============================================================
# CurriculumSubject
# ============================================================
@admin.register(CurriculumSubject)
class CurriculumSubjectAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm

    list_display = (
        "curriculum",
        "subject",
        "year_level",
        "semester",
        "category",
        "book_count",
        "view_books",
    )
    list_filter = (
        ("curriculum", RelatedDropdownFilter),
        ("subject", RelatedDropdownFilter),
        ("year_level", ChoicesDropdownFilter),
        ("category", ChoicesDropdownFilter),
    )
    list_filter_submit = True
    search_fields = (
        "curriculum__name",
        "curriculum__program__abbreviation",
        "subject__code",
        "subject__title",
    )
    autocomplete_fields = ("curriculum", "subject", "books")

    @admin.display(description="Books")
    def book_count(self, obj):
        return obj.books.count()

    @admin.display(description="Books")
    def view_books(self, obj):
        url = (
            reverse("admin:book_book_changelist")
            + f"?curriculum_subjects__id__exact={obj.pk}"
        )
        return format_html(
            '<a href="{}" class="inline-flex items-center gap-1.5 px-3 py-1 '
            'text-xs font-medium rounded bg-primary-600 text-white '
            'hover:bg-primary-700 transition">'
            '<span>View Books</span>'
            "</a>",
            url,
        )