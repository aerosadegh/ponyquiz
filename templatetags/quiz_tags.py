from django import template
from django.template.loader import render_to_string
from ponyquiz.models import *

register = template.Library()

@register.filter
def user_notes(question, num=3):
    return UserNote.objects.filter(question=question).order_by("-created_on")

@register.simple_tag
def user_notes_form(question):
    return render_to_string("ponyquiz/user_notes_form.html", locals())
