from django.http import HttpResponseRedirect
from gdata.urlfetch import HttpResponse
from models import *
from django.contrib import admin
from django import forms

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
    def get_urls(self):
        urls = super(ModuleOptions, self).get_urls()
        my_urls = patterns('',
            (r'^import/$', self.import_csv)
        )
        return my_urls + urls

    def import_definitions(self, request, template_name='ponyquiz/'):

        class DefinitionListForm(forms.Form):
            module_title = forms.CharField()
            question_content = forms.CharField(
                initial="<p>What character is this?:<div class='hiragana'>%s</div></p>",
                help_text="content to place the definition in, "
                "wherever you place %s the word or symbol being defined will be inserted.")
            definitions = forms.TextField(
                initial=u"&#x3042;, a",
                help_text="Please write definitions one per line here<br />"
                "Symbol or word first then the definition separated with a comma")

        if request.method == "POST":
            form = DefinitionListForm(request.POST)
            if form.is_valid():
                module = Module.objects.get_or_create(name=form.cleaned_data['module_title'])
                for definition in form.cleaned_data['definitions'].split():
                    symbol, definition = definition.split(",")
                    question = Question(
                        content=form.cleaned_data['question_content'] % hira,
                        module=module,  module_answers=True)
                    question.save()
                    PossibleAnswer(content=roma, question=question).save()
                return HttpResponseRedirect("..")
        else:
            form = DefinitionListForm()
admin.site.register(Question, QuestionOptions)
admin.site.register(Quiz, QuizOptions)
admin.site.register(Module, ModuleOptions)

