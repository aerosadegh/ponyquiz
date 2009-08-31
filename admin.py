from models import *
from django.contrib import admin

class Module_Inline(admin.TabularInline):
    model = Module

class QuizModule_Inline(admin.TabularInline):
    model = QuizModule

class QuizModule_Inline(admin.TabularInline):
    model = QuizModule

class PossibleAnswer_Inline(admin.TabularInline):
    model = PossibleAnswer
    extra = 5

class QuizSession_Inline(admin.TabularInline):
    model = QuizSession

class QuestionOptions(admin.ModelAdmin):
    inlines = [PossibleAnswer_Inline]
    tiny_mce_fields = ("content",)

class QuizOptions(admin.ModelAdmin):
    inlines = [QuizModule_Inline]
    prepopulated_fields = { "slug": ("name",) }
    tiny_mce_fields = ("description",)

class ModuleOptions(admin.ModelAdmin):
    pass

admin.site.register(Question, QuestionOptions)
admin.site.register(Quiz, QuizOptions)
admin.site.register(Module, ModuleOptions)

