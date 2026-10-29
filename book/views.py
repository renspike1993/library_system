from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from administrative.models import Department, Program
from book.models import Book, Collection, Section
from compliance.models import Report
from library_service.models import Transaction, TransactionDetail
from students.models import Student


# ============================================================
# Dashboard
# ============================================================
def dashboard_callback(request, context):
    counts = {
        "books": Book.objects.count(),
        "students": Student.objects.count(),
        "transactions": Transaction.objects.count(),
        "transaction_details": TransactionDetail.objects.count(),
        "collections": Collection.objects.count(),
        "sections": Section.objects.count(),
        "departments": Department.objects.count(),
        "programs": Program.objects.count(),
        "reports": Report.objects.count(),
        "users": get_user_model().objects.count(),
    }

    status_counts = (
        TransactionDetail.objects.values("status").annotate(count=Count("id"))
    )
    status_map = {row["status"]: row["count"] for row in status_counts}

    context.update({
        "counts": counts,
        "status_map": status_map,
        "books_per_department": Department.objects.annotate(
            book_count=Count("programs__books", distinct=True)
        ).order_by("-book_count")[:5],
        "books_per_collection": Collection.objects.annotate(
            book_count=Count("books", distinct=True)
        ).order_by("-book_count")[:5],
        "students_per_department": Department.objects.annotate(
            student_count=Count("students", distinct=True)
        ).order_by("-student_count")[:5],
        "recent_transactions": Transaction.objects.select_related(
            "student"
        ).order_by("-created_at")[:5],
        "top_books": Book.objects.annotate(
            borrow_count=Count("transaction_details")
        ).filter(borrow_count__gt=0).order_by("-borrow_count")[:5],
    })
    return context


class DashboardView(TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return dashboard_callback(self.request, context)


# ============================================================
# OPAC
# ============================================================
class OPACView(TemplateView):
    template_name = "opac.html"
    DEFAULT_LIMIT = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()
        context["query"] = query

        if query:
            context["books"] = (
                Book.objects.filter(
                    Q(title_statement__icontains=query)
                    | Q(author_personal__icontains=query)
                    | Q(isbn__icontains=query)
                )
                .select_related("collection", "program")
                .order_by("title_statement")
                .distinct()[:50]
            )
            context["is_default"] = False
        else:
            context["books"] = (
                Book.objects.select_related("collection", "program")
                .order_by("-created_at")[: self.DEFAULT_LIMIT]
            )
            context["is_default"] = True

        return context


# ============================================================
# Book Detail (ISBD + MARC21 + Normal)
# ============================================================
class BookDetailView(TemplateView):
    template_name = "book_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Added prefetch_related("copies") to load barcodes efficiently
        book = get_object_or_404(
            Book.objects.select_related("collection", "program", "section").prefetch_related("copies"),
            pk=kwargs["pk"],
        )
        
        context["book"] = book
        context["marc_fields"] = _build_marc21(book)
        context["isbd"] = _build_isbd(book)
        return context


# ============================================================
# Helper Functions
# ============================================================
def _build_marc21(book):
    """Return a list of (tag, label, value) for non-empty MARC21 fields."""
    rows = []

    def add(tag, label, value):
        if value:
            rows.append((tag, label, value))

    add("000", "Leader", book.leader)
    add("001", "Control Number", book.control_number)
    add("003", "Control Number Identifier", book.control_number_identifier)
    add("008", "Fixed-Length Data Elements", book.fixed_length_data)
    add("020", "ISBN", book.isbn)
    add("022", "ISSN", book.issn)
    add("040", "Cataloging Source", book.cataloging_source)
    add("041", "Language Code", book.language_code)
    add("050", "LC Call Number", book.lcc_number)
    add("082", "Dewey Decimal Classification", book.ddc_number)
    add("100", "Main Entry — Personal Name", book.author_personal)
    add("110", "Main Entry — Corporate Name", book.author_corporate)
    add("245", "Title Statement", book.title_statement or book.title)
    add("245 $b", "Remainder of Title", book.subtitle)
    add("245 $c", "Statement of Responsibility", book.responsibility_statement)
    add("250", "Edition Statement", book.edition_statement)
    add("264 $a", "Place of Publication", book.publication_place)
    add("264 $b", "Publisher", book.publisher)
    add("264 $c", "Date of Publication", book.publication_date)
    add("300 $a", "Extent", book.extent)
    add("300 $b", "Other Physical Details", book.physical_details)
    add("300 $c", "Dimensions", book.dimensions)
    add("336", "Content Type", book.content_type)
    add("337", "Media Type", book.media_type)
    add("338", "Carrier Type", book.carrier_type)
    add("490", "Series Statement", book.series_statement)
    add("500", "General Note", book.general_note)
    add("504", "Bibliography Note", book.bibliography_note)
    add("520", "Summary", book.summary)
    add("650", "Topical Subject", book.subjects)
    add("700", "Added Entry — Personal Name", book.added_authors)
    
    # Fetch Accession Numbers and Copy Count from BookCopy
    copies = book.copies.all()
    if copies.exists():
        accession_nos = ", ".join([c.accession_number for c in copies])
        add("852 $p", "Accession Numbers", accession_nos)
        add("852 $t", "Total Copies", copies.count())

    add("856 $u", "Electronic Location", book.electronic_location)
    return rows


def _build_isbd(book):
    """Build an ISBD-style citation string."""
    parts = []

    if book.author_personal:
        parts.append(f"{book.author_personal}.")
    
    title = book.title_statement or book.title
    if book.subtitle:
        title += f" : {book.subtitle}"
    if book.responsibility_statement:
        title += f" / {book.responsibility_statement}"
    parts.append(f"{title}.")

    if book.edition_statement:
        parts.append(f"{book.edition_statement}.")

    pub = []
    if book.publication_place:
        pub.append(book.publication_place)
    if book.publisher:
        pub.append(book.publisher)
    if book.publication_date:
        pub.append(book.publication_date)
    if pub:
        parts.append(" : ".join(pub) + ".")

    phys = []
    if book.extent:
        phys.append(book.extent)
    if book.physical_details:
        phys.append(f": {book.physical_details}")
    if book.dimensions:
        phys.append(f"; {book.dimensions}")
    if phys:
        parts.append(" ".join(phys) + ".")

    if book.series_statement:
        parts.append(f"({book.series_statement}).")

    if book.general_note:
        parts.append(f"{book.general_note}.")

    if book.isbn:
        parts.append(f"ISBN {book.isbn}.")

    return " ".join(parts)


# ============================================================
# TV Ads
# ============================================================
class TVAdsView(TemplateView):
    template_name = "tv_ads.html"


# ============================================================
# Turnstile Gate
# ============================================================
class TurnstileGateView(TemplateView):
    template_name = "turnstile_gate.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["latest_books"] = Book.objects.order_by("-created_at")[:5]
        return context