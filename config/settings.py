import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,192.168.10.170").split(",")

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.import_export", 
    "unfold.contrib.filters",
    # 'jazzmin', 
    # 'tailwind', 
    'channels',
    'liveload',
    "import_export",  # Must be added
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Local apps
    "administrative",
    "book",
    "students",

    "library_service",
    "compliance",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS":[BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
# ASGI_APPLICATION = "config.asgi.application"
# settings.py
ASGI_APPLICATION = 'config.routing.application'


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Manila"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"   # required for collectstatic in production

import os

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.templatetags.static import static

# Helper to check if a user has ANY of the permissions in a group
def has_any_perm(user, perm_list):
    if user.is_superuser:
        return True
    return any(user.has_perm(p) for p in perm_list)

def navigation_callback(request):
    user = request.user

    # Define all possible items and their required permissions
    # Format: (Title, Icon, URL, required_permission)
    # If required_permission is None, everyone can see it.
    
    groups = [
        {
            "title": _("Main Options"),
            "items": [
                (_("OPAC"), "local_library", reverse_lazy("opac"), None),
                (_("TV Ads"), "tv", reverse_lazy("tv_ads"), None),
                (_("Turnstile Gate"), "lock", reverse_lazy("turnstile_gate"), None),
                (_("Scanner"), "lock", reverse_lazy("scanner"), None),

            ]
        },
        {
            "title": _("Organization"),
            "items": [
                (_("Departments"), "account_tree", reverse_lazy("admin:administrative_department_changelist"), "administrative.view_department"),
                (_("Programs"), "school", reverse_lazy("admin:administrative_program_changelist"), "administrative.view_program"),
                (_("Curricula"), "list_alt", reverse_lazy("admin:administrative_curriculum_changelist"), "administrative.view_curriculum"),
                (_("Subjects"), "book_2", reverse_lazy("admin:administrative_subject_changelist"), "administrative.view_subject"),
                (_("Curriculum Subjects"), "checklist", reverse_lazy("admin:administrative_curriculumsubject_changelist"), "administrative.view_curriculumsubject"),
            ]
        },
        {
            "title": _("Catalog Management"),
            "items": [
                (_("Books"), "menu_book", reverse_lazy("admin:book_book_changelist"), "book.view_book"),
                (_("Book Copies"), "content_copy", reverse_lazy("admin:book_bookcopy_changelist"), "book.view_bookcopy"),
                (_("Collections"), "folder_open", reverse_lazy("admin:book_collection_changelist"), "book.view_collection"),
                (_("Sections"), "shelves", reverse_lazy("admin:book_section_changelist"), "book.view_section"),
            ]
        },
        {
            "title": _("Patron Members"),
            "items": [
                (_("Students"), "badge", reverse_lazy("admin:students_student_changelist"), "students.view_student"),
            ]
        },
        {
            "title": _("Circulation"),
            "items": [
                (_("Transactions"), "swap_horiz", reverse_lazy("admin:library_service_transaction_changelist"), "library_service.view_transaction"),
                (_("Transaction Details"), "receipt_long", reverse_lazy("admin:library_service_transactiondetail_changelist"), "library_service.view_transactiondetail"),
                (_("Turnstile Logs"), "sensor_door", reverse_lazy("admin:library_service_turnstilelog_changelist"), "library_service.view_turnstilelog"),
            ]
        },
        {
            "title": _("CHED Compliance"),
            "items": [
                (_("Reports"), "description", reverse_lazy("admin:compliance_report_changelist"), "compliance.view_report"),
            ]
        },
        {
            "title": _("Access Control"),
            "items": [
                (_("Users"), "person", reverse_lazy("admin:auth_user_changelist"), "auth.view_user"),
                (_("Groups & Roles"), "group", reverse_lazy("admin:auth_group_changelist"), "auth.view_group"),
            ]
        },
    ]

    navigation = []
    
    for group in groups:
        # Filter items based on permission
        visible_items = []
        for title, icon, link, perm in group["items"]:
            if perm is None or user.is_superuser or user.has_perm(perm):
                visible_items.append({
                    "title": title,
                    "icon": icon,
                    "link": link,
                })
        
        # Only add the group if there are visible items inside
        if visible_items:
            navigation.append({
                "title": group["title"],
                "separator": True,
                "collapsible": True,
                "collapsed": True,
                "items": visible_items,
            })
            
    return navigation

UNFOLD = {
    "SITE_TITLE": "MOIST Library System",
    "SITE_HEADER": "MLMS",
    "SITE_SUBHEADER": "Library Management System",
    "SITE_URL": "/",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SITE_ICON": lambda request: static("img/logo.png"),
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        # Pass the function here so Unfold evaluates it on every request
        "navigation": lambda request: navigation_callback(request),
    },
}