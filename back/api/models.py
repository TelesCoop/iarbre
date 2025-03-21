from django.db import models


class Feedback(models.Model):
    """Store feedbacks from carte.iarbre.fr"""

    email = models.EmailField(blank=True, null=True)
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.email or 'Anonymous'}"


# Create your models here.
