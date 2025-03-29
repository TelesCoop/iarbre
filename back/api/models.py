from django.db import models


class TimeStampedModel(models.Model):
    """An abstract base class model that provides self-updating `created` and `modified` fields."""

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Feedback(TimeStampedModel):
    """Store feedbacks from carte.iarbre.fr"""

    email = models.EmailField(blank=True, null=True)
    feedback = models.TextField()

    def __str__(self):
        return f"Feedback from {self.email or 'Anonymous'}"
