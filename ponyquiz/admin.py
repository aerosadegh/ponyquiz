from quiz.models import *
from django.contrib import admin

class Module_Inline(admin.TabularInline):
    model = Module

class QuizModule_Inline(admin.TabularInline):
    model = QuizModule

class QuizModule_Inline(admin.TabularInline):
    model = QuizModule

class PossibleAnswer_Inline(admin.TabularInline):
    model = PossibleAnswer

class HelpNote_Inline(admin.TabularInline):
    model = HelpNote

class UserNote_Inline(admin.TabularInline):
    model = UserNote

class UserNote_Inline(admin.TabularInline):
    model = UserNote

class UserNoteVote_Inline(admin.TabularInline):
    model = UserNoteVote

class QuizSession_Inline(admin.TabularInline):
    model = QuizSession

class UserAnswer_Inline(admin.TabularInline):
    model = UserAnswer

class UserLongAnswerOptions(admin.ModelAdmin):
    pass

class QuizModuleOptions(admin.ModelAdmin):
    pass

class QuestionOptions(admin.ModelAdmin):
    inlines = [HelpNote_Inline]

class QuizOptions(admin.ModelAdmin):
    inlines = [QuizModule_Inline]

class UserAnswerOptions(admin.ModelAdmin):
    pass

class MultipleChoiceQuestionOptions(admin.ModelAdmin):
    pass

class QuizSessionOptions(admin.ModelAdmin):
    pass

class PossibleAnswerOptions(admin.ModelAdmin):
    pass

class ModuleOptions(admin.ModelAdmin):
    pass


admin.site.register(UserLongAnswer, UserLongAnswerOptions)
admin.site.register(QuizModule, QuizModuleOptions)
admin.site.register(Question, QuestionOptions)
admin.site.register(Quiz, QuizOptions)
admin.site.register(UserAnswer, UserAnswerOptions)
admin.site.register(MultipleChoiceQuestion, MultipleChoiceQuestionOptions)
admin.site.register(QuizSession, QuizSessionOptions)
admin.site.register(PossibleAnswer, PossibleAnswerOptions)
admin.site.register(Module, ModuleOptions)

