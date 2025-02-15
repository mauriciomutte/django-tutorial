from rest_framework import serializers

from polling.apps.core.models import Choice, Question, Vote


class QuestionSerializer(serializers.ModelSerializer):
    choices = serializers.SerializerMethodField()

    def get_choices(self, obj):
        return obj.choices.values("id", "choice_text")

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


class VoteSerializer(serializers.Serializer):
    poll_id = serializers.UUIDField()
    choice_id = serializers.UUIDField()
    session_id = serializers.CharField(required=False, allow_null=True)

    def validate(self, attrs):
        try:
            question = Question.objects.get(id=attrs["poll_id"])
            choice = Choice.objects.get(id=attrs["choice_id"])

            # Validate choice belongs to question
            if choice.question_id != question.id:
                raise serializers.ValidationError("Choice does not belong to this poll")

            # Validate if user has already voted
            if attrs["session_id"]:
                prev_vote = Vote.objects.filter(
                    question=question, session_id=attrs["session_id"]
                )

                if prev_vote.exists():
                    raise serializers.ValidationError("You have already voted")

            attrs["question"] = question
            attrs["choice"] = choice

            return attrs

        except Question.DoesNotExist:
            raise serializers.ValidationError("Poll not found")
        except Choice.DoesNotExist:
            raise serializers.ValidationError("Choice not found")
