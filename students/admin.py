from django.contrib import admin

from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RelatedDropdownFilter, FieldTextFilter
from unfold.contrib.import_export.forms import ImportForm, ExportForm

from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget

from administrative.models import Department
from .models import Student


# --- Custom widget: create Department if missing ---
class CreatingDepartmentWidget(ForeignKeyWidget):
    """
    Look up Department by abbreviation. If it doesn't exist, create it.
    Your Department model requires `description`, so we default it to the
    abbreviation when creating.
    """

    def clean(self, value, row=None, **kwargs):
        if not value:
            return None
        value = str(value).strip()
        obj, _created = self.model.objects.get_or_create(
            abbreviation=value,
            defaults={"description": value},
        )
        return obj


# --- Import/Export resource ---
class StudentResource(resources.ModelResource):
    department = fields.Field(
        column_name="department",
        attribute="department",
        widget=CreatingDepartmentWidget(Department, field="abbreviation"),
    )

    class Meta:
        model = Student
        import_id_fields = ("student_id",)
        fields = (
            "student_id",
            "first_name",
            "middle_name",
            "last_name",
            "department",
        )
        skip_unchanged = False
        report_skipped = True
        raise_errors = False


@admin.register(Student)
class StudentAdmin(ModelAdmin, ImportExportModelAdmin):
    resource_class = StudentResource
    import_form_class = ImportForm
    export_form_class = ExportForm

    list_display = (
        "student_id",
        "last_name",
        "first_name",
        "middle_name",
        "department",
    )

    list_filter = (
        ("department", RelatedDropdownFilter),
        ("student_id", FieldTextFilter),
        ("last_name", FieldTextFilter),
    )
    list_filter_submit = True
    search_fields = ("student_id", "first_name", "middle_name", "last_name")
    autocomplete_fields = ("department",)
    list_per_page = 25

    fieldsets = (
        (
            "Identification",
            {"fields": ("student_id",)},
        ),
        (
            "Personal Information",
            {"fields": ("first_name", "middle_name", "last_name")},
        ),
        (
            "Academic",
            {"fields": ("department",)},
        ),
    )