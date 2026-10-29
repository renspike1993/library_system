from django.db import models


class Collection(models.Model):
    description = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["description"]

    def __str__(self):
        return self.description


class Section(models.Model):
    """A physical shelf location in the library."""

    description = models.CharField(max_length=255)

    class Meta:
        ordering = ["description"]

    def __str__(self):
        return f"{self.description} "


class Book(models.Model):
    """
    A bibliographic record. Fields map to MARC21 tags (see help_text).
    Repeatable MARC fields (650, 700, 020...) are stored one value per line.
    The CSV import columns are also supported (see help_text for CSV names).
    """

    class BookCategory(models.TextChoices):
        ACADEMIC = "academic library", "Academic Library"
        SCHOOL = "school library", "School Library"

    book_category = models.CharField(
        max_length=20,
        choices=BookCategory.choices,
        default=BookCategory.ACADEMIC,
        help_text="Category of the library this book belongs to.",
    )

    # --- Library-specific relations -------------------------------------
    program = models.ForeignKey(
        "administrative.Program",
        on_delete=models.PROTECT,
        related_name="books",
        null=True,
        blank=True,
    )
    collection = models.ForeignKey(
        Collection,
        on_delete=models.PROTECT,
        related_name="books",
        null=True,
        blank=True,
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="books",
    )
    cover_img = models.ImageField(upload_to="covers/", blank=True, null=True)

    # --- Control fields (0XX) -------------------------------------------
    leader = models.CharField("Leader (000)", max_length=24, blank=True)
    control_number = models.CharField(
        "Control number (001 / CSV: control_no)",
        max_length=50,
        null=True,
        blank=True,
    )
    control_number_identifier = models.CharField(
        "Control number ID (003)", max_length=50, blank=True
    )
    fixed_length_data = models.CharField(
        "Fixed-length data elements (008)", max_length=40, blank=True
    )
    date_time_stamp = models.DateTimeField(
        "CSV: date_time_stamp", null=True, blank=True
    )

    # --- Standard numbers / call numbers (0XX) ---------------------------
    isbn = models.CharField("ISBN (020 $a)", max_length=20, blank=True, db_index=True)
    issn = models.CharField("ISSN (022 $a)", max_length=9, blank=True)
    price = models.DecimalField(
        "Price (CSV: price)",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    cataloging_source_a = models.CharField("CSV: cataloging_source_a", max_length=100, blank=True)
    cataloging_source_b = models.CharField("CSV: cataloging_source_b", max_length=100, blank=True)
    cataloging_source_e = models.CharField("CSV: cataloging_source_e", max_length=100, blank=True)
    cataloging_source = models.CharField(
        "Cataloging source (040)", max_length=100, blank=True
    )
    language_code = models.CharField(
        "Language code (041 $a)", max_length=10, blank=True
    )
    lcc_number = models.CharField("LC call number (050)", max_length=100, blank=True)
    call_number = models.CharField("CSV: call_number", max_length=100, blank=True)
    ddc_number = models.CharField("Dewey Decimal (082)", max_length=50, blank=True)

    # --- Main entry (1XX) -----------------------------------------------
    author_personal = models.CharField(
        "Main entry - personal name (100 / CSV: main_author)",
        max_length=255,
        blank=True,
    )

    main_author = models.CharField("CSV: main_author", max_length=255, blank=True)

    author_corporate = models.CharField(
        "Main entry - corporate name (110)", max_length=255, blank=True
    )
    main_corporate_name = models.CharField(
        "CSV: main_corporate_name", max_length=255, blank=True
    )

    title_statement = models.CharField("CSV: title_statement", max_length=500, blank=True)
    subtitle = models.CharField(
        "Remainder of title (245 $b)", max_length=500, blank=True
    )
    responsibility_statement = models.CharField(
        "Statement of responsibility (245 $c)", max_length=500, blank=True
    )
    title_author = models.CharField("CSV: title_author", max_length=500, blank=True)
    edition_statement = models.CharField(
        "Edition (250)", max_length=100, blank=True
    )
    edition = models.CharField("CSV: edition", max_length=100, blank=True)

    # --- Publication (26X) -----------------------------------------------
    publication_place = models.CharField(
        "Place of publication (264 $a)", max_length=255, blank=True
    )
    pub_place = models.CharField("CSV: pub_place", max_length=255, blank=True)
    publisher = models.CharField("Publisher (264 $b)", max_length=255, blank=True)
    publication_date = models.CharField(
        "Date of publication (264 $c)", max_length=50, blank=True
    )
    pub_year = models.CharField("CSV: pub_year", max_length=50, blank=True)
    publication_distribution = models.CharField(
        "CSV: publication_distribution", max_length=255, blank=True
    )

    # --- Physical description (3XX) -------------------------------------
    extent = models.CharField(
        "Extent / pages (300 $a)", max_length=100, blank=True
    )
    pages = models.CharField("CSV: pages", max_length=100, blank=True)
    physical_details = models.CharField(
        "Other physical details (300 $b)", max_length=100, blank=True
    )
    illustrations = models.CharField("CSV: illustrations", max_length=100, blank=True)
    dimensions = models.CharField(
        "Dimensions (300 $c)", max_length=50, blank=True
    )
    size = models.CharField("CSV: size", max_length=50, blank=True)
    volume = models.CharField("CSV: volume", max_length=50, blank=True)
    content_type = models.CharField(
        "Content type (336)", max_length=50, blank=True, default="text"
    )
    content_code = models.CharField("CSV: content_code", max_length=50, blank=True)
    media_type = models.CharField(
        "Media type (337)", max_length=50, blank=True, default="unmediated"
    )
    media_code = models.CharField("CSV: media_code", max_length=50, blank=True)
    carrier_type = models.CharField(
        "Carrier type (338)", max_length=50, blank=True, default="volume"
    )
    carrier_code = models.CharField("CSV: carrier_code", max_length=50, blank=True)

    # --- Series (4XX) ----------------------------------------------------
    series_statement = models.CharField(
        "Series statement (490)", max_length=255, blank=True
    )
    series_title = models.CharField("CSV: series_title", max_length=255, blank=True)

    # --- Notes (5XX) -----------------------------------------------------
    general_note = models.TextField("General note (500)", blank=True)
    bibliography_note = models.TextField("Bibliography note (504)", blank=True)
    summary = models.TextField("Summary / abstract (520)", blank=True)

    # --- Subject access (6XX) -- one per line ----------------------------
    subjects = models.TextField(
        "Topical subjects (650) - one per line", blank=True
    )
    subject_topic = models.TextField("CSV: subject_topic", blank=True)
    subject_form = models.CharField("CSV: subject_form", max_length=255, blank=True)
    genre = models.CharField("CSV: genre", max_length=255, blank=True)
    genre_form = models.CharField("CSV: genre_form", max_length=255, blank=True)
    topical_term = models.TextField("CSV: topical_term", blank=True)
    geographical_name = models.CharField(
        "CSV: geographical_name", max_length=255, blank=True
    )
    chronological_term = models.CharField(
        "CSV: chronological_term", max_length=255, blank=True
    )
    faceted_topical_terms = models.TextField(
        "CSV: faceted_topical_terms", blank=True
    )
    subject_corporate_name = models.CharField(
        "CSV: subject_corporate_name", max_length=255, blank=True
    )
    subject_personal_name = models.CharField(
        "CSV: subject_personal_name", max_length=255, blank=True
    )
    uniform_title = models.CharField(
        "CSV: uniform_title", max_length=255, blank=True
    )

    # --- Added entries (7XX) -- one per line -----------------------------
    added_authors = models.TextField(
        "Added entry - personal names (700) - one per line", blank=True
    )
    added_entry_elements = models.TextField(
        "CSV: added_entry_elements", blank=True
    )
    corporate_name = models.CharField("CSV: corporate_name", max_length=255, blank=True)
    personal_name = models.CharField("CSV: personal_name", max_length=255, blank=True)

    # --- Holdings / location (85X) ---------------------------------------
    # accession_number = models.CharField(
    #     "Accession number / barcode (852 $p)", max_length=50
    # )
    # accession_no = models.CharField("CSV: accession_no", max_length=50, blank=True)
    copy_number = models.PositiveSmallIntegerField(
        "Copy number (852 $t)", default=1
    )

    electronic_location = models.URLField(
        "Electronic location (856 $u)", blank=True
    )

    # --- Provenance / acquisition ----------------------------------------
    source_vendor = models.CharField("CSV: source_vendor", max_length=255, blank=True)
    source_date = models.DateField("CSV: source_date", null=True, blank=True)
    acquisition_type_id = models.CharField(
        "CSV: acquisition_type_id", max_length=50, blank=True
    )
    acquisition_custom = models.TextField("CSV: acquisition_custom", blank=True)

    # --- Library / classification extras ---------------------------------
    library_name = models.CharField("CSV: library_name", max_length=255, blank=True)
    year = models.CharField("CSV: year", max_length=20, blank=True)
    course = models.CharField("CSV: course", max_length=255, blank=True)
    curriculum = models.CharField("CSV: curriculum", max_length=255, blank=True)

    # --- Physical copy tracking ------------------------------------------
    barcode = models.CharField("CSV: barcode", max_length=100, blank=True)
    rfid = models.CharField("CSV: rfid", max_length=100, blank=True)
    availability = models.BooleanField("CSV: availability", default=True)
    reserved = models.BooleanField("CSV: reserved", default=False)

    # --- Soft-delete / archive -------------------------------------------
    archived_at = models.DateTimeField("CSV: archived_at", null=True, blank=True)
    deleted_at = models.DateTimeField("CSV: deleted_at", null=True, blank=True)

    # --- Audit ----------------------------------------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title_statement"]

    def __str__(self):
        return self.title_statement


# Add this anywhere below your Book model (e.g., at the very bottom of the file)

class BookCopy(models.Model):
    """
    Represents a physical, individual copy of a Book.
    Allows tracking of multiple copies with their own accession numbers and statuses.
    """
    
    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        BORROWED = "borrowed", "Borrowed"
        RESERVED = "reserved", "Reserved"
        LOST = "lost", "Lost"

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="copies",
        verbose_name="Book",
    )
    accession_number = models.CharField(
        "Accession Number",
        max_length=50,
        unique=True,
        help_text="The unique physical barcode/accession number for this specific copy."
    )


    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
        db_index=True,
    )
    acquired_date = models.DateField(
        "Acquired Date",
        null=True,
        blank=True,
        help_text="Date this specific copy was acquired by the library."
    )

    class Meta:
        ordering = ["book__title_statement", "accession_number"]
        verbose_name = "Book Copy"
        verbose_name_plural = "Book Copies"
    


    def __str__(self):
        # Use standard Python slicing instead of template filters
        title = self.book.title_statement or self.book.title or "Untitled"
        short_title = title[:30] + ("..." if len(title) > 30 else "")
        return f"{self.accession_number} - {short_title} ({self.get_status_display()})"


