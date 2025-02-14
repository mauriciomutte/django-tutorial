from rest_framework import serializers

from polling.apps.core.models import Question


class QuestionSerializer(serializers.ModelSerializer):
    choices = serializers.SerializerMethodField()

    def get_choices(self, obj):
        return obj.choices.values_list("choice_text", flat=True)

    class Meta:
        model = Question
        fields = ["id", "question_text", "pub_date", "choices"]


class CreatePollSerializer(serializers.Serializer):
    question_text = serializers.CharField()
    pub_date = serializers.DateTimeField()
    choices = serializers.ListField(
        child=serializers.CharField(),
        min_length=2,  # Ensure at least 2 choices are provided
    )
