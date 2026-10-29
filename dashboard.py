from django.contrib.auth import get_user_model
from django.db.models import Count, Sum

from administrative.models import Department, Program
from book.models import Book, Collection, Section
from compliance.models import Report
from library_service.models import Transaction, TransactionDetail
from students.models import Student


def dashboard_callback(request, context):
    """
    Build the summary data for the Unfold dashboard.
    Returned dict is merged into the admin index context.
    """

    # --- Counts per model ---
    counts = {
        "departments": Department.objects.count(),
        "programs": Program.objects.count(),
        "books": Book.objects.count(),
        "collections": Collection.objects.count(),
        "sections": Section.objects.count(),
        "students": Student.objects.count(),
        "transactions": Transaction.objects.count(),
        "transaction_details": TransactionDetail.objects.count(),
        "reports": Report.objects.count(),
        "users": get_user_model().objects.count(),
    }

    # --- Transaction status breakdown ---
    status_counts = (
        TransactionDetail.objects
        .values("status")
        .annotate(count=Count("id"))
        .order_by("status")
    )
    status_map = {row["status"]: row["count"] for row in status_counts}

    # --- Books per department (top 5) ---
    books_per_department = (
        Department.objects
        .annotate(book_count=Count("programs__books", distinct=True))
        .order_by("-book_count")[:5]
    )

    # --- Books per collection (top 5) ---
    books_per_collection = (
        Collection.objects
        .annotate(book_count=Count("books", distinct=True))
        .order_by("-book_count")[:5]
    )

    # --- Recent transactions (last 5) ---
    recent_transactions = (
        Transaction.objects
        .select_related("student")
        .order_by("-created_at")[:5]
    )

    # --- Most borrowed books (top 5) ---
    top_books = (
        Book.objects
        .annotate(borrow_count=Count("transaction_details"))
        .filter(borrow_count__gt=0)
        .order_by("-borrow_count")[:5]
    )

    # --- Students per department (top 5) ---
    students_per_department = (
        Department.objects
        .annotate(student_count=Count("students", distinct=True))
        .order_by("-student_count")[:5]
    )

    context.update(
        {
            "counts": counts,
            "status_map": status_map,
            "books_per_department": books_per_department,
            "books_per_collection": books_per_collection,
            "recent_transactions": recent_transactions,
            "top_books": top_books,
            "students_per_department": students_per_department,
        }
    )
    return context