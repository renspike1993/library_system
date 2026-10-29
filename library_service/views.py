import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from students.models import Student
from .models import TurnstileLog
from liveload import ProgressTracker

@csrf_exempt # Allows your hardware scanner to POST without a CSRF token
def scan_gate_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            student_id = data.get("student_id")
            direction = data.get("direction", "entry") # 'entry' or 'exit'

            # 1. Find the student
            student = Student.objects.get(student_id=student_id)

            # 2. Save the log
            TurnstileLog.objects.create(
                student=student,
                log_type=direction
            )

            # 3. TRIGGER THE LIVE WEBSOCKET UPDATE
            tracker = ProgressTracker("turnstile_live")
            tracker.update(message="New scan", percent=100)

            return JsonResponse({"status": "success", "message": "Scan logged"})
            
        except Student.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Student not found"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)

from django.shortcuts import render
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from liveload import ProgressTracker
from students.models import Student
from .models import TurnstileLog

@staff_member_required
def scanner_page(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id", "").strip()
        log_type = request.POST.get("log_type", "entry")

        if student_id:
            try:
                student = Student.objects.get(student_id=student_id)
                
                # 1. Save the log to the database
                TurnstileLog.objects.create(
                    student=student,
                    log_type=log_type
                )
                
                # 2. Trigger the WebSocket for the Turnstile Display page
                tracker = ProgressTracker("turnstile_live")
                tracker.update(message="New scan", percent=100)

                messages.success(request, f"Scan recorded for {student.full_name} ({log_type.upper()})")
                
            except Student.DoesNotExist:
                messages.error(request, f"Student with ID '{student_id}' not found.")
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")

    return render(request, "scanner.html")

from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from .models import TurnstileLog
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from .models import TurnstileLog
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from .models import TurnstileLog

from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from .models import TurnstileLog


@staff_member_required
def latest_scan(request):
    log = (
        TurnstileLog.objects
        .select_related("student", "student__department")   # ← prefetch to avoid N+1
        .order_by("-time")
        .first()
    )

    if not log:
        return JsonResponse({"id": None})

    student = log.student

    # Safely turn the Department object into a string
    dept = getattr(student, "department", None)
    dept_name = "—"
    if dept is not None:
        dept_name = (
            getattr(dept, "name", None)
            or getattr(dept, "code", None)
            or getattr(dept, "description", None)
            or str(dept)
        )

    return JsonResponse({
        "name":       student.full_name,
        "id":         student.student_id,
        "department": dept_name,                             # ← now a string
        "avatar": (
            student.avatar.url
            if getattr(student, "avatar", None)
            else f"https://api.dicebear.com/7.x/avataaars/svg"
                 f"?seed={student.student_id}&backgroundColor=fdf2f3"
        ),
        "direction":  log.log_type,
        "time":       log.time.isoformat(),
        "entry_count": TurnstileLog.objects.filter(log_type="entry").count(),
        "exit_count":  TurnstileLog.objects.filter(log_type="exit").count(),
    })