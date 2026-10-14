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


class ShortLink(TimeStampedModel):
    """Short code pointing to a front-end map path with its query string"""

    code = models.CharField(max_length=12, unique=True)
    path = models.CharField(max_length=2000, db_index=True)

    def __str__(self):
        return f"{self.code} -> {self.path}"
