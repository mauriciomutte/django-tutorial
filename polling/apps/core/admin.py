from django.contrib import admin

from .models import Choice, Question, Vote


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    def choice_count(self, obj):
        # Use cached_property to avoid repeated DB queries
        if not hasattr(obj, "_choice_count"):
            obj._choice_count = obj.choices.count()
        return obj._choice_count

    choice_count.short_description = "Number of choices"
    readonly_fields = ["id"]
    fields = ["id", "question_text", "pub_date"]
    inlines = [ChoiceInline]
    list_display = ("question_text", "pub_date", "choice_count")
    list_filter = ["pub_date"]
    search_fields = ["question_text"]


admin.site.register(Vote)
