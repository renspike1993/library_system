from datetime import timedelta

from django.db import models


class Report(models.Model):
    class ReportType(models.TextChoices):
        ATTENDANCE = "attendance", "Attendance"
        BOOKS = "books", "Book Hooldings"
        STUDENTS = "students", "Student Logs"
        TRANSACTIONS = "transactions", "Transactions Logs"


    class DateRange(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"
        YEARLY = "yearly", "Yearly"

    description = models.CharField(max_length=255)
    report_type = models.CharField(max_length=20, choices=ReportType.choices)
    date_range = models.CharField(max_length=10, choices=DateRange.choices)
    starting_from = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-starting_from"]

    @property
    def ending_on(self):
        days = {"daily": 1, "weekly": 7, "monthly": 30, "yearly": 365}[self.date_range]
        return self.starting_from + timedelta(days=days - 1)

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.get_date_range_display()} from {self.starting_from}"
