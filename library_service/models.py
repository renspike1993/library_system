import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


def generate_transaction_code():
    """e.g. TXN-20261020-A1B2C3D4"""
    return f"TXN-{timezone.now():%Y%m%d}-{uuid.uuid4().hex[:8].upper()}"


class Transaction(models.Model):
    transaction_code = models.CharField(
        max_length=30, unique=True, editable=False, default=generate_transaction_code
    )
    description = models.CharField(max_length=255, blank=True)
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.PROTECT,
        related_name="transactions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.transaction_code


class TransactionDetail(models.Model):
    class Status(models.TextChoices):
        RETURNED = "returned", "Returned"
        BORROWED = "borrowed", "Borrowed"
        RESERVED = "reserved", "Reserved"
        LOST = "lost", "Lost"

    transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, related_name="details"
    )
    
    # CHANGED: Now links to the specific physical copy
    book_copy = models.ForeignKey(
        "book.BookCopy", 
        on_delete=models.PROTECT, 
        related_name="transaction_details"
    )
    
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.BORROWED
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        # Optional: Show the Book title along with the Accession Number
        title = self.book_copy.book.title_statement or self.book_copy.book.title
        return f"{self.transaction} - {title} [{self.book_copy.accession_number}] ({self.status})"


class TurnstileLog(models.Model):
    """
    Records physical entry and exit scans at the library turnstile gate.
    """
    class LogType(models.TextChoices):
        ENTRY = "entry", "Entry"
        EXIT = "exit", "Exit"

    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="turnstile_logs",
        help_text="The student who scanned their ID."
    )
    log_type = models.CharField(
        max_length=10,
        choices=LogType.choices,
        default=LogType.ENTRY,
        db_index=True,
    )
    time = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="The exact time the scan occurred."
    )

    class Meta:
        ordering = ["-time"]
        verbose_name = "Turnstile Log"
        verbose_name_plural = "Turnstile Logs"

    def __str__(self):
        return f"{self.student.student_id} - {self.get_log_type_display()} ({self.time.strftime('%Y-%m-%d %H:%M:%S')})"