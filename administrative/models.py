from django.db import models


# ============================================================
# Department
# ============================================================
class Department(models.Model):
    abbreviation = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=255)

    class Meta:
        ordering = ["abbreviation"]

    def __str__(self):
        return self.abbreviation


# ============================================================
# Program
# ============================================================
class Program(models.Model):
    abbreviation = models.CharField(max_length=20, unique=True)

    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name="programs"
    )

    description = models.CharField(max_length=255)

    class Meta:
        ordering = ["abbreviation"]

    def __str__(self):
        return f"{self.abbreviation} ({self.department.abbreviation})"


# ============================================================
# Curriculum
# ============================================================
class Curriculum(models.Model):
    """
    A curriculum (e.g., BSIT 2024, BSCS 2018) belongs to a program
    and groups the subjects a student must take.
    """

    program = models.ForeignKey(
        Program, on_delete=models.CASCADE, related_name="curricula"
    )
    name = models.CharField(
        max_length=100,
        help_text="e.g., BSIT 2024, BSCS 2018",
    )
    effective_year = models.CharField(
        max_length=20,
        blank=True,
        help_text="Academic year the curriculum took effect",
    )
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["program__abbreviation", "-effective_year", "name"]
        verbose_name_plural = "Curricula"
        constraints = [
            models.UniqueConstraint(
                fields=["program", "name"],
                name="unique_curriculum_per_program",
            )
        ]

    def __str__(self):
        return f"{self.program.abbreviation} — {self.name}"


# ============================================================
# Subject
# ============================================================
class Subject(models.Model):
    """
    A subject/course (e.g., IT 101 – Introduction to Computing).
    Subjects are reusable across curricula.
    """

    code = models.CharField(
        max_length=30,
        unique=True,
        help_text="e.g., IT 101, MATH 101",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    units = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=3.0,
        help_text="Credit units (e.g., 3.0)",
    )

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} — {self.title}"


# ============================================================
# CurriculumSubject (join table)
# ============================================================
class CurriculumSubject(models.Model):
    """
    Links a Subject to a Curriculum, with the year level and
    whether it is required or elective.
    """

    class YearLevel(models.IntegerChoices):
        FIRST = 1, "1st Year"
        SECOND = 2, "2nd Year"
        THIRD = 3, "3rd Year"
        FOURTH = 4, "4th Year"
        FIFTH = 5, "5th Year"

    class Category(models.TextChoices):
        REQUIRED = "required", "Required"
        ELECTIVE = "elective", "Elective"

    curriculum = models.ForeignKey(
        Curriculum, on_delete=models.CASCADE, related_name="subjects"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.PROTECT, related_name="curricula"
    )
    year_level = models.PositiveSmallIntegerField(
        choices=YearLevel.choices,
        default=YearLevel.FIRST,
    )
    semester = models.CharField(
        max_length=20,
        blank=True,
        help_text="e.g., 1st Semester, 2nd Semester, Summer",
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.REQUIRED,
    )

    books = models.ManyToManyField(
        "book.Book",
        related_name="curriculum_subjects",
        blank=True,
        help_text="Books assigned to this curriculum subject",
    )
    class Meta:
        ordering = ["year_level", "semester", "subject__code"]
        constraints = [
            models.UniqueConstraint(
                fields=["curriculum", "subject"],
                name="unique_subject_per_curriculum",
            )
        ]

    def __str__(self):
        return (
            f"{self.curriculum} — {self.subject.code} "
            f"(Y{self.year_level})"
        )