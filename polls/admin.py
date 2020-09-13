"""customize apps for the admin site"""

from django.contrib import admin

from .models import Choice, Question

class ChoiceInLine(admin.TabularInline):
    """displays the Choice model data in-line on the Question admin window"""
    model = Choice
    extra = 1

class QuestionAdmin(admin.ModelAdmin):
    """Customizes the Question model"""
    fieldsets = [
        (None, {'fields': ['question_text']}),
        ('Date Information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInLine]
    list_display = ('question_text', 'pub_date', 'was_published_recently')
    list_filter = ['pub_date']
    search_fields = ['question_text']

admin.site.register(Question, QuestionAdmin)
