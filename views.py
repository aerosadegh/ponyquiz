from models import *
from django.template.context import RequestContext
from django.shortcuts import render_to_response
# Create your views here.

def quiz_start(request, slug, template_name="ponyquiz/quiz_start.html"):

    quiz = Quiz.objects.get(slug=slug)

    # is this user already participating in a quiz?

    if request.method == "POST":
        # start quiz!
        pass


    return render_to_response(template_name, locals(),
        context_instance=RequestContext(request))