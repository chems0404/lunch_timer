from django.contrib import admin
from .models import Collaborator, LunchRecord


@admin.register(Collaborator)
class CollaboratorAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(LunchRecord)
class LunchRecordAdmin(admin.ModelAdmin):
    list_display = (
        "collaborator",
        "date",
        "start_time",
        "end_time",
        "display_duration",
        "display_exceeded",
    )
    list_filter = ("date", "collaborator")
    search_fields = ("collaborator__name",)
    readonly_fields = ("created_at", "updated_at")

    def display_duration(self, obj):
        return str(obj.duration).split(".")[0] if obj.duration else "-"

    display_duration.short_description = "Duración"

    def display_exceeded(self, obj):
        return "Sí" if obj.exceeded_one_hour else "No"

    display_exceeded.short_description = "Excedió 1 hora"