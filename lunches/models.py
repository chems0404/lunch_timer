from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class Collaborator(models.Model):
    name = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class LunchRecord(models.Model):
    collaborator = models.ForeignKey(
        Collaborator,
        on_delete=models.PROTECT,
        related_name="lunch_records",
    )
    date = models.DateField(default=timezone.localdate)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    MAX_DURATION = timedelta(hours=1)

    class Meta:
        ordering = ["-date", "collaborator__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["collaborator", "date"],
                name="unique_lunch_per_collaborator_per_day",
            )
        ]

    def __str__(self):
        return f"{self.collaborator} - {self.date}"

    @property
    def is_active(self):
        return self.start_time and not self.end_time

    @property
    def duration(self):
        if not self.start_time:
            return None

        end = self.end_time or timezone.now()
        return end - self.start_time

    @property
    def exceeded_one_hour(self):
        duration = self.duration
        return bool(duration and duration > self.MAX_DURATION)

    def clean(self):
        if self.end_time and self.end_time < self.start_time:
            raise ValidationError("La hora de fin no puede ser anterior al inicio.")