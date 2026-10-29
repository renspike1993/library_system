from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import (
    ChoicesDropdownFilter,
    RelatedDropdownFilter,
    RangeDateFilter, # Added for filtering logs by date
)

# Import all your models, including the new TurnstileLog
from .models import Transaction, TransactionDetail, TurnstileLog


# ============================================================
# Transaction & Transaction Detail
# ============================================================

class TransactionDetailInline(TabularInline):
    model = TransactionDetail
    extra = 0
    autocomplete_fields = ("book_copy",)
    fields = ("book_copy", "status")


@admin.register(Transaction)
class TransactionAdmin(ModelAdmin):
    list_display = (
        "transaction_code",
        "student",
        "description",
        "detail_count",
        "created_at",
    )
    readonly_fields = ("transaction_code", "created_at")
    search_fields = (
        "transaction_code",
        "description",
        "student__student_id",
        "student__last_name",
        "student__first_name",
    )
    list_filter = (
        ("student", RelatedDropdownFilter),
    )
    list_filter_submit = True
    autocomplete_fields = ("student",)
    inlines = [TransactionDetailInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_detail_count=Count("details", distinct=True))

    @admin.display(description="Details", ordering="_detail_count")
    def detail_count(self, obj):
        return obj._detail_count


@admin.register(TransactionDetail)
class TransactionDetailAdmin(ModelAdmin):
    list_display = (
        "transaction",
        "borrower",
        "book_copy",
        "status_badge",
        "updated_at",
    )
    list_filter = (
        ("status", ChoicesDropdownFilter),
        ("transaction", RelatedDropdownFilter),
        ("book_copy", RelatedDropdownFilter),
    )
    list_filter_submit = True
    search_fields = (
        "transaction__transaction_code",
        "transaction__student__student_id",
        "transaction__student__last_name",
        "transaction__student__first_name",
        "book_copy__accession_number",
        "book_copy__book__title", # Fixed: changed from title_statement to title
    )
    autocomplete_fields = ("transaction", "book_copy")
    readonly_fields = ("updated_at",)

    STATUS_STYLES = {
        TransactionDetail.Status.RETURNED: (
            "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
        ),
        TransactionDetail.Status.BORROWED: (
            "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
        ),
        TransactionDetail.Status.RESERVED: (
            "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200"
        ),
        TransactionDetail.Status.LOST: (
            "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200"
        ),
    }

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            "transaction__student", 
            "book_copy__book"
        )

    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        classes = self.STATUS_STYLES.get(
            obj.status, "bg-gray-100 text-gray-800"
        )
        return format_html(
            '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full '
            'text-xs font-medium {}">{}</span>',
            classes,
            obj.get_status_display(),
        )

    @admin.display(
        description="Borrower",
        ordering="transaction__student__last_name",
    )
    def borrower(self, obj):
        student = obj.transaction.student
        if not student:
            return "—"
        return format_html(
            '<div class="leading-tight">'
            '<div class="text-sm font-medium text-gray-900 dark:text-gray-100">{}</div>'
            '<div class="text-xs text-gray-500 dark:text-gray-400">{}</div>'
            "</div>",
            student.full_name,
            student.student_id,
        )

from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from liveload import ProgressTracker

from .models import Transaction, TransactionDetail, TurnstileLog
from students.models import Student
from unfold.admin import ModelAdmin

@admin.register(TurnstileLog)
class TurnstileLogAdmin(ModelAdmin):
    list_display = ("time", "student", "log_type")
    list_filter = ("log_type",)
    search_fields = ("student__student_id", "student__first_name", "student__last_name")
    
    # ... your existing TurnstileLogAdmin code ...

    # =========================================================
    # CUSTOM SCANNER VIEW
    # =========================================================
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "scanner/",
                self.admin_site.admin_view(self.scanner_view),
                name="library_service_turnstilelog_scanner",
            ),
        ]
        return custom_urls + urls

    def scanner_view(self, request):
        if request.method == "POST":
            student_id = request.POST.get("student_id", "").strip()
            log_type = request.POST.get("log_type", "entry")

            if student_id:
                try:
                    student = Student.objects.get(student_id=student_id)
                    
                    # 1. Save the log
                    TurnstileLog.objects.create(
                        student=student,
                        log_type=log_type
                    )
                    
                    # 2. Trigger the LiveLoad WebSocket for the Turnstile Display
                    tracker = ProgressTracker("turnstile_live")
                    tracker.update(message="New scan", percent=100)

                    messages.success(request, f"Scan recorded for {student.full_name} ({log_type.upper()})")
                    
                except Student.DoesNotExist:
                    messages.error(request, f"Student with ID '{student_id}' not found.")
                except Exception as e:
                    messages.error(request, f"Error: {str(e)}")

        context = {
            **self.admin_site.each_context(request),
            "title": "Turnstile Scanner",
            "opts": self.model._meta,
        }
        return render(request, "admin/library_service/turnstilelog/scanner.html", context)