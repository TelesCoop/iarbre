from rest_framework import serializers
from iarbre_data.models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["id", "email", "feedback", "created_at"]
