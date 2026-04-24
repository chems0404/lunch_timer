import csv

from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required

from .models import Collaborator, LunchRecord


# ======================
# KIOSCO
# ======================

def kiosk_home(request):
    collaborators = Collaborator.objects.filter(is_active=True)

    return render(request, "lunches/kiosk_home.html", {
        "collaborators": collaborators
    })


def collaborator_status(request, collaborator_id):
    collaborator = get_object_or_404(
        Collaborator,
        id=collaborator_id,
        is_active=True
    )

    today = timezone.localdate()

    lunch = LunchRecord.objects.filter(
        collaborator=collaborator,
        date=today
    ).first()

    return render(request, "lunches/collaborator_status.html", {
        "collaborator": collaborator,
        "lunch": lunch
    })


def start_lunch(request, collaborator_id):
    if request.method != "POST":
        return redirect("kiosk_home")

    collaborator = get_object_or_404(
        Collaborator,
        id=collaborator_id,
        is_active=True
    )

    today = timezone.localdate()

    try:
        LunchRecord.objects.create(
            collaborator=collaborator,
            date=today,
            start_time=timezone.now()
        )
        messages.success(request, "Almuerzo iniciado.")
    except IntegrityError:
        messages.error(request, "Ya registraste almuerzo hoy.")

    return redirect("collaborator_status", collaborator_id=collaborator.id)


def end_lunch(request, collaborator_id):
    if request.method != "POST":
        return redirect("kiosk_home")

    collaborator = get_object_or_404(
        Collaborator,
        id=collaborator_id,
        is_active=True
    )

    today = timezone.localdate()

    lunch = LunchRecord.objects.filter(
        collaborator=collaborator,
        date=today
    ).first()

    if not lunch:
        messages.error(request, "No hay almuerzo iniciado.")
    elif lunch.end_time:
        messages.warning(request, "Ya finalizaste.")
    else:
        lunch.end_time = timezone.now()
        lunch.save()
        messages.success(request, "Almuerzo finalizado.")

    return redirect("collaborator_status", collaborator_id=collaborator.id)


# ======================
# DASHBOARD ADMIN
# ======================

@staff_member_required
def admin_dashboard(request):
    today = timezone.localdate()

    selected_date = request.GET.get("date") or today.isoformat()
    selected_collaborator = request.GET.get("collaborator", "")
    only_exceeded = request.GET.get("exceeded", "")

    records = LunchRecord.objects.select_related("collaborator").filter(
        date=selected_date
    )

    if selected_collaborator:
        records = records.filter(collaborator_id=selected_collaborator)

    # aplicar filtro excedidos
    if only_exceeded == "1":
        records = [r for r in records if r.exceeded_one_hour]

    collaborators = Collaborator.objects.all()

    total_records = len(records)
    active_lunches = sum(1 for r in records if r.is_active)
    exceeded_lunches = sum(1 for r in records if r.exceeded_one_hour)

    return render(request, "lunches/admin_dashboard.html", {
        "records": records,
        "collaborators": collaborators,
        "selected_date": selected_date,
        "selected_collaborator": selected_collaborator,
        "only_exceeded": only_exceeded,
        "total_records": total_records,
        "active_lunches": active_lunches,
        "exceeded_lunches": exceeded_lunches,
    })


# ======================
# EXPORTAR CSV
# ======================

@staff_member_required
def export_lunches_csv(request):
    selected_date = request.GET.get("date")
    selected_collaborator = request.GET.get("collaborator", "")
    only_exceeded = request.GET.get("exceeded", "")

    records = LunchRecord.objects.select_related("collaborator").all()

    if selected_date:
        records = records.filter(date=selected_date)

    if selected_collaborator:
        records = records.filter(collaborator_id=selected_collaborator)

    if only_exceeded == "1":
        records = [r for r in records if r.exceeded_one_hour]

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="reporte_almuerzos.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Colaborador",
        "Fecha",
        "Inicio",
        "Fin",
        "Duracion",
        "Excedio 1 hora",
        "Notas administrativas",
    ])

    for record in records:
        writer.writerow([
            record.collaborator.name,
            record.date,
            timezone.localtime(record.start_time).strftime("%H:%M:%S"),
            timezone.localtime(record.end_time).strftime("%H:%M:%S") if record.end_time else "",
            str(record.duration).split(".")[0] if record.duration else "",
            "Si" if record.exceeded_one_hour else "No",
            record.admin_notes,
        ])

    return response