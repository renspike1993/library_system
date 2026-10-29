from import_export import resources, fields, widgets
# ... other imports ...
from .models import Book, Collection, Section
from import_export import resources, fields, widgets
from django.db import transaction
from .models import Book, BookCopy

class BookResource(resources.ModelResource):
    # We map the CSV columns to the fields
    title = fields.Field(column_name="title_statement", attribute="title")
    author = fields.Field(column_name="title_author", attribute="title_author")
    accession = fields.Field(column_name="accession_no", attribute="accession_number")
    barcode = fields.Field(column_name="barcode", attribute="barcode")

    class Meta:
        model = Book
        # Exclude the primary key and timestamps so Django handles them
        exclude = ("id", "created_at", "updated_at")
        skip_unchanged = True
        report_skipped = True

    def before_save_instance(self, instance, row, **kwargs):
        """
        Check if the Book already exists based on Title and Author.
        If it does, attach the instance to the existing book.
        """
        if instance.title and instance.title_author:
            # Check if a book with this exact title and author exists
            existing_book = Book.objects.filter(
                title__iexact=instance.title.strip(),
                title_author__iexact=instance.title_author.strip()
            ).first()

            if existing_book:
                # Point the instance to the existing book's primary key
                instance.pk = existing_book.pk
                instance.id = existing_book.id

    def after_save_instance(self, instance, row, **kwargs):
        """
        After the Book is saved (whether new or existing), create the BookCopy.
        """
        accession_no = row.get("accession_no")
        barcode_val = row.get("barcode")

        # Only create a copy if an accession number is provided
        if accession_no:
            # Check if this specific copy already exists to prevent duplicates
            if not BookCopy.objects.filter(accession_number=accession_no).exists():
                BookCopy.objects.create(
                    book=instance,
                    accession_number=accession_no,
                    status=BookCopy.Status.AVAILABLE
                )