import uuid

from django.db import transaction
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from polling.apps.core.models import Choice, Question, Vote

from .serializers import CreatePollSerializer, QuestionSerializer, VoteSerializer


# get poll by id
class PollDetailView(APIView):
    """
    Retrieve a poll by its ID.

    Accepts a GET request with a poll ID and returns the poll data.

    Returns:
        200: Successfully retrieved poll
            {
                "id": int,
                "question_text": str,
                "pub_date": datetime
            }
        404: Poll not found
            {
                "detail": "Not found"
            }

    Example:
        GET /api/v1/polls/1/
    """

    def get(self, request, pk):
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = QuestionSerializer(question)
        return Response(serializer.data)


class PollCreateView(APIView):
    """
    Create a new poll question with choices.

    Accepts a POST request with a question text and creates a new poll in the system.

    Request Body:
        {
            "question_text": str  # The text of the poll question,
            "pub_date": datetime  # The date and time the poll was published
            "choices": str[]  # The choices of the poll
        }

    Returns:
        201: Successfully created poll
            {
                "id": int,
                "question_text": str,
                "pub_date": datetime
            }
        400: Bad Request
            {
                "field_name": [
                    "error message"
                ]
            }

    Example:
        POST /api/v1/poll/
        {
            "question_text": "What is your favorite color?",
            "pub_date": "2024-01-01T00:00:00Z",
            "choices": ["Red", "Blue", "Green"]
        }
    """

    def post(self, request):
        serializer = CreatePollSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # Create the question
                question = Question.objects.create(
                    question_text=serializer.validated_data["question_text"],
                    pub_date=serializer.validated_data["pub_date"],
                )

                # Create choices using bulk_create for better performance
                choices = [
                    Choice(question=question, choice_text=choice_text)
                    for choice_text in serializer.validated_data["choices"]
                ]
                Choice.objects.bulk_create(choices)

                response_serializer = QuestionSerializer(question)
                return Response(
                    response_serializer.data, status=status.HTTP_201_CREATED
                )
        except Exception as e:
            return Response(
                {"detail": f"Error creating poll: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PollVoteView(APIView):
    """
    Vote for a choice in a poll.

    Accepts a POST request with a poll ID and a choice ID, and updates the vote count for the choice.

    Request Body:
        {
            "poll_id": int,
            "choice_id": int,
            "session_id": str
        }

    Returns:
        200: Successfully voted
        400: Bad Request
            {
                "field_name": [
                    "error message"
                ]
            }

    Example:
        POST /api/v1/poll/vote/
        {
            "poll_id": 1,
            "choice_id": 1,
            "session_id": "123"
        }
    """

    def post(self, request, id):
        try:
            session_id = request.COOKIES.get("session_id")
            data = {
                "poll_id": id,
                "choice_id": request.data.get("choice_id"),
                "session_id": session_id,
            }

            serializer = VoteSerializer(data=data)
            serializer.is_valid(raise_exception=True)

            # Create new session if needed
            if not session_id:
                session_id = str(uuid.uuid4())

            # Create the vote
            Vote.objects.create(
                question=serializer.validated_data["question"],
                choice=serializer.validated_data["choice"],
                session_id=session_id,
            )

            response = Response(
                {"detail": "Vote recorded successfully"}, status=status.HTTP_201_CREATED
            )

            # Set cookie only if new session
            if not request.COOKIES.get("session_id"):
                response.set_cookie(
                    key="session_id",
                    value=session_id,
                    max_age=60 * 60 * 24 * 7,  # 7 days
                    httponly=True,
                    secure=True,
                    samesite="Lax",
                    path="/",
                )

            return response

        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {"detail": "An error occurred while processing your vote"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
