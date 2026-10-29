from django.db import models
from administrative.models import Department

class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    department = models.ForeignKey(
        "administrative.Department",
        on_delete=models.PROTECT,
        related_name="students",
    )



    class Meta:
        ordering = ["last_name", "first_name"]
        verbose_name = "Student"
        verbose_name_plural = "Students"

    def __str__(self):
        return f"{self.student_id} - {self.last_name}, {self.first_name}"

    @property
    def full_name(self):
        parts = [self.first_name, self.middle_name, self.last_name]
        return " ".join(p for p in parts if p)