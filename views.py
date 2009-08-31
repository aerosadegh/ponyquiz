from django.http import HttpResponse
import datetime
from django import forms
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Sum
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from models import *

def build_sample():

    Question.objects.all().delete()
    
    romanji = [
        ('a', u'&#x3042;'), ('i', u'&#x3044;'), ('u', u'&#x3046;'), ('e', u'&#x3048;'), ('o', u'&#x304A;'),
        ('ka', u'&#x304B;'), ('ki', u'&#x304D;'), ('ku', u'&#x304F;'), ('ke', u'&#x3051;'), ('ko', u'&#x3053;'),
        ('sa', u'&#x3055;'), ('shi', u'&#x3057;'), ('su', u'&#x3059;'), ('se', u'&#x305B;'), ('so', u'&#x305D;'),
        ('ta', u'&#x305F;'), ('chi', u'&#x3061;'), ('tsu', u'&#x3064;'), ('te', u'&#x3066;'), ('to', u'&#x3068;'),
        ('na', u'&#x306A;'), ('ni', u'&#x306B;'), ('nu', u'&#x306C;'), ('ne', u'&#x306D;'), ('no', u'&#x306E;'),
        ('ha', u'&#x306F;'), ('hi', u'&#x3072;'), ('hu', u'&#x3075;'), ('he', u'&#x3078;'), ('ho', u'&#x307B;'),
        ('ma', u'&#x307E;'), ('mi', u'&#x307F;'), ('mu', u'&#x3080;'), ('me', u'&#x3081;'), ('mo', u'&#x3082;'),
        ('ra', u'&#x3089;'), ('ri', u'&#x308A;'), ('ru', u'&#x308B;'), ('re', u'&#x308C;'), ('ro', u'&#x308D;'),
        ('ga', u'&#x304C;'), ('gi', u'&#x304E;'), ('gu', u'&#x3050;'), ('ge', u'&#x3052;'), ('go', u'&#x3054;'),
        ('za', u'&#x3056;'), ('ji', u'&#x3058;'), ('zu', u'&#x305A;'), ('ze', u'&#x305C;'), ('zo', u'&#x305E;'),
        ('da', u'&#x3060;'), ('ji', u'&#x3062;'), ('zu', u'&#x3065;'), ('de', u'&#x3067;'), ('do', u'&#x3069;'),
        ('ba', u'&#x3070;'), ('bi', u'&#x3073;'), ('bu', u'&#x3076;'), ('be', u'&#x3079;'), ('bo', u'&#x307C;'),
        ('pa', u'&#x3071;'), ('pi', u'&#x3074;'), ('pu', u'&#x3077;'), ('pe', u'&#x307A;'), ('po', u'&#x307D;'),
        ('ya', u'&#x3084;'), ('yu', u'&#x3086;'), ('yo', u'&#x3088;'),
        ('wa', u'&#x308F;'), ('wo', u'&#x3092;'),
        ('n', u'&#x3093;')
    ]

    hiragana,created = Module.objects.get_or_create(name="Hiragana", defaults={"description": "Hiragana"})
    if created:
        QuizModule(quiz=quiz, module=hiragana).save()
    for roma, hira in romanji:
        question = Question(
            title=u"Hiragana Recognition",
            content=u"<p>What character is this?:<div class='hiragana'>%s</div></p>"%hira,
            module=hiragana)
        question.save()
        for roma2, hira2 in romanji:
            answer = PossibleAnswer(content=roma2, question=question)
            if roma == roma2:
                answer.percent_correct = 1
            answer.save()
            print u" - answer %s" % hira2
        print u"question %s" % hira


def quiz_intro(request, slug, template_name="ponyquiz/quiz_start.html"):

    quiz = Quiz.objects.get(slug=slug)
    topscores = QuizSession.objects.order_by("-total_score")[:10]
    total_plays = QuizSession.objects.count()

    # is this user already participating in a quiz?
    open_sessions = QuizSession.objects.filter(
        user=request.user, ended_on__isnull=True)

    class NameForm(forms.Form):
        name = forms.CharField(label="Name", initial=request.user.username)

    if request.method == "POST":
        form = NameForm(request.POST)
        if form.is_valid():
            # create a quiz session
            session = QuizSession()
            if request.user.is_authenticated():
                session.user = request.user
            else:
                session.ip_address = request.META['REMOTE_ADDR']
            session.name = form.cleaned_data['name']
            session.quiz = quiz
            session.attempt = QuizSession.objects.filter(
                user=request.user, quiz=quiz).count() + 1
            session.save()

            first = None

            # register all questions to it
            for quizmodule in quiz.quizmodule_set.all():

                for question in quizmodule.get_questions():
                    ua = UserAnswer()
                    ua.session = session
                    ua.question = question
                    ua.save()
                    if not first:
                        first = ua

            return HttpResponseRedirect(reverse("quiz-question", args=[first.id]))
    else:
        form = NameForm()

    return render_to_response(template_name, locals(),
        context_instance=RequestContext(request))

def quiz_end(request, id, template_name="ponyquiz/quiz_end.html"):
    session = QuizSession.objects.get(id=id)
    if not session.ended_on:
        session.ended_on = datetime.datetime.now()
        session.total_score = session.useranswer_set.aggregate(score=Sum("score"))["score"]
        session.save()

    # show congrats/apologize
    topscores = QuizSession.objects.order_by("-total_score")[:10]
    rank = QuizSession.objects.filter(total_score__gt=session.total_score).count() + 1
    total_plays = QuizSession.objects.count()
    

    return render_to_response(template_name, locals(),
        context_instance=RequestContext(request))

def quiz_question(request, id, template_name="ponyquiz/quiz_question.html"):

    # preload all the goodness
    response = UserAnswer.objects.filter(session__user=request.user).select_related().get(id=id)
    session = response.session

    # get the next and previous questions
    responses = session.useranswer_set.all()
    for idx, item in enumerate(responses.all()):
        if item.id == response.id:
            break            
    if idx > 0:
        previous = responses[idx-1]
    if idx+1 < responses.count():
        next = responses[idx+1]

    unanswered = responses.filter(answered_on__isnull=True)
    if unanswered.exclude(id=response.id).count() > 0:
        next_unanswered = unanswered.exclude(id=response.id)[0]
    else:
        next_unanswered = None
    answered = responses.filter(answered_on__isnull=False)
    previous_answers = ("%s" % response.previous_answers).split(",")
    question = response.question
    
    quiz_module = QuizModule.objects.get(module__question=question)
    message = ""
    
    if request.method == "POST" and request.POST.get('answer', False):
        
        if not response.answered_on:
            answer = request.POST.get("answer")
            score,answer = question.correct(answer)
            response.answer = answer

            # if the module requires a correct answer,
            # then don't set it as answered
            if quiz_module.must_answer and score > 0:
                response.answered_on = datetime.datetime.now()
                if response.attempt == 1:
                    response.score = score
                    message = "Correct!"
                else:
                    response.score = 0
                    message = "Correct, but sorry, no points"
            else:
                message = "Sorry, that's incorrect"
                response.attempt += 1
                if response.previous_answers:
                    response.previous_answers += ",%s" % answer
                else:
                    response.previous_answers = answer

            response.save()

        if not next_unanswered:
            return HttpResponseRedirect(reverse("quiz-end", args=[session.id]))
#        else:
#            return HttpResponseRedirect(reverse("quiz-question", args=[next_unanswered.id]))
    
    return render_to_response(template_name, locals(),
        context_instance=RequestContext(request))

def add_usernote(request):

    class UserNoteForm(forms.ModelForm):
        class Meta:
            model = UserNote
            exclude = ["user"]


    form = UserNoteForm(request.REQUEST)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.user = request.user
        obj.save()
        return HttpResponse("Saved")

    return HttpResponse(unicode(form.errors))