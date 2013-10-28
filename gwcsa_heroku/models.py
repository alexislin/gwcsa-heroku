from django.db import models

class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=True)

class WorkShift(TimestampedModel):
    season = models.PositiveIntegerField(null=False,default=2014)

