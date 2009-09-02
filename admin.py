from django.template.context import RequestContext
from django.http import HttpResponseRedirect
from django.conf.urls.defaults import *
from models import *
from django.contrib import admin
from django.shortcuts import render_to_response
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
            (r'^import-definitions/$', self.import_definitions)
        )
        return my_urls + urls

    def import_definitions(self, request, template_name='ponyquiz/import_definitions.html'):

        class DefinitionListForm(forms.Form):
            module_title = forms.CharField()
            question_content = forms.CharField(
                initial="<p>What character is this?:<div class='hiragana'>%s</div></p>",
                help_text="content to place the definition in, "
                "wherever you place %s the word or symbol being defined will be inserted.",
                widget=forms.TextInput(attrs={"size": 60})
            )
            definitions = forms.CharField(
                initial=u"&#x3042;, a",
                help_text="Please write definitions one per line here<br />"
                "Symbol or word first then the definition separated with a comma",
                widget=forms.Textarea
            )

        if request.method == "POST":
            form = DefinitionListForm(request.POST)
            if form.is_valid():
                module, created = Module.objects.get_or_create(name=form.cleaned_data['module_title'])
                if not created:
                    module.question_set.all().delete()
                definitions = form.cleaned_data['definitions'].split("\r\n")
                for definition in definitions:
                    if definition.strip():
                        symbol, definition = definition.split(",")
                        symbol = symbol.strip()
                        definition = definition.strip()
                        question = Question(
                            content=form.cleaned_data['question_content'] % symbol,
                            module=module,  module_answers=True)
                        question.save()
                        PossibleAnswer(content=definition, question=question).save()
                return HttpResponseRedirect("..")
        else:
            form = DefinitionListForm()

        return render_to_response(template_name, locals(),
            context_instance=RequestContext(request))
admin.site.register(Question, QuestionOptions)
admin.site.register(Quiz, QuizOptions)
admin.site.register(Module, ModuleOptions)
admin.site.register(UserPossibleAnswer)
admin.site.register(PossibleAnswer)

