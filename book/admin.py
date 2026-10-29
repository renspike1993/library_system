from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RelatedDropdownFilter
from unfold.contrib.import_export.forms import ImportForm, ExportForm
from import_export.admin import ImportExportModelAdmin

from .models import Book, Collection, Section, BookCopy


# ============================================================
# Inlines
# ============================================================
class BookCopyInline(TabularInline):
    model = BookCopy
    extra = 0
    fields = ("accession_number", "status", "acquired_date")


# ============================================================
# BookCopy Admin
# ============================================================
@admin.register(BookCopy)
class BookCopyAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm

    list_display = ("accession_number", "book", "status", "acquired_date")
    list_filter = (
        ("status", ChoicesDropdownFilter),
        ("book__collection", RelatedDropdownFilter),
    )
    list_filter_submit = True
    search_fields = (
        "accession_number", 
        "book__title_statement", 
        "book__title", 
    )
    autocomplete_fields = ("book",)


# ============================================================
# Collection Admin
# ============================================================
@admin.register(Collection)
class CollectionAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm

    search_fields = ("description",)
    list_display = ("description", "get_book_count", "view_books")
    list_filter = ("description",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_book_count=Count("books"))

    @admin.display(description="Number of Books", ordering="_book_count")
    def get_book_count(self, obj):
        return obj._book_count

    @admin.display(description="Books")
    def view_books(self, obj):
        url = (
            reverse("admin:book_book_changelist")
            + f"?collection__id__exact={obj.pk}"
        )
        return format_html(
            '<a href="{}" class="inline-flex items-center gap-1 px-3 py-1 '
            'text-xs font-medium rounded bg-primary-600 text-white '
            'hover:bg-primary-700 transition">View Books</a>',
            url,
        )


# ============================================================
# Section Admin
# ============================================================
@admin.register(Section)
class SectionAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm

    list_display = ("description", "get_book_count", "view_books")
    search_fields = ("description",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_book_count=Count("books"))

    @admin.display(description="Book Counts", ordering="_book_count")
    def get_book_count(self, obj):
        return obj._book_count

    @admin.display(description="Books")
    def view_books(self, obj):
        url = (
            reverse("admin:book_book_changelist")
            + f"?section__id__exact={obj.pk}"
        )
        return format_html(
            '<a href="{}" class="inline-flex items-center gap-1 px-3 py-1 '
            'text-xs font-medium rounded bg-primary-600 text-white '
            'hover:bg-primary-700 transition">View Books</a>',
            url,
        )


# ============================================================
# Book Admin
# ============================================================
@admin.register(Book)
class BookAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    inlines = [BookCopyInline]

    list_display = (
        "id",
        "cover_preview",
        "title_statement",
        "main_author",
        "pub_year",
        "program",
        "collection",
        "section",
    )

    list_display_links = ("id",)
    list_filter = (
        ("program", RelatedDropdownFilter),
        ("collection", RelatedDropdownFilter),
    )

    search_fields = (
        "title_statement",
        "title_author",
        "isbn",
        "subjects",
    )
    list_filter_submit = True
    list_per_page = 25

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "program",
                    "book_category",
                    "collection",
                    "section",
                    "cover_img",
                    "copy_number",
                )
            },
        ),
        (
            "Control fields (0XX)",
            {
                "classes": ("collapse",),
                "fields": (
                    "leader",
                    "control_number",
                    "control_number_identifier",
                    "fixed_length_data",
                ),
            },
        ),
        (
            "Numbers & classification (0XX)",
            {
                "classes": ("collapse",),
                "fields": (
                    "isbn",
                    "issn",
                    "cataloging_source",
                    "language_code",
                    "lcc_number",
                    "ddc_number",
                ),
            },
        ),
        (
            "Main entry (1XX)",
            {
                "classes": ("collapse",),
                "fields": ("author_personal", "author_corporate"),
            },
        ),
        (
            "Title & edition (24X-25X)",
            {
                "classes": ("collapse",),
                "fields": (
                    "title_statement",
                    "subtitle",
                    "main_author",
                    "responsibility_statement",
                    "edition_statement",
                ),
            },
        ),
        (
            "Publication (26X)",
            {
                "classes": ("collapse",),
                "fields": (
                    "publication_place",
                    "publisher",
                    "pub_year",
                ),
            },
        ),
        (
            "Physical description (3XX)",
            {
                "classes": ("collapse",),
                "fields": (
                    "extent",
                    "physical_details",
                    "dimensions",
                    "content_type",
                    "media_type",
                    "carrier_type",
                ),
            },
        ),
        (
            "Series (4XX)",
            {"classes": ("collapse",), "fields": ("series_statement",)},
        ),
        (
            "Notes (5XX)",
            {
                "classes": ("collapse",),
                "fields": ("general_note", "bibliography_note", "summary"),
            },
        ),
        (
            "Access points (6XX-7XX)",
            {"classes": ("collapse",), "fields": ("subjects", "added_authors")},
        ),
        (
            "Electronic location (856)",
            {"classes": ("collapse",), "fields": ("electronic_location",)},
        ),
    )

    @admin.display(description="Cover")
    def cover_preview(self, obj):
        if obj.cover_img:
            return format_html(
                '<img src="{}" alt="cover" '
                'style="width:48px;height:64px;object-fit:cover;'
                'border-radius:4px;box-shadow:0 1px 2px rgba(0,0,0,.15);" />',
                obj.cover_img.url,
            )
        return mark_safe(
            '<div style="width:48px;height:64px;display:flex;align-items:center;'
            'justify-content:center;background:#e5e7eb;color:#6b7280;'
            'border-radius:4px;font-size:10px;">N/A</div>'
        )

    def lookup_allowed(self, lookup, value, request):
        if lookup in (
            "program__department__id__exact",
            "curriculum_subjects__id__exact",
        ):
            return True
        return super().lookup_allowed(lookup, value, request)