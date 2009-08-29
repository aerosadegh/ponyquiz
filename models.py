from django.db import models
from tagging import fields as tagging
from django.conf import settings
import random

MAX_CHOICES = getattr(settings, "QUIZ_MAX_CHOICES", 5)

# Create your models here.
class Quiz(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField()
    tags = tagging.TagField()

    class Meta:
        verbose_name_plural = "Quizes"
        ordering = ["name"]

    def __unicode__(self):
        return self.name

class Module(models.Model):
    parent = models.ForeignKey("self", null=True, blank=True)
    name = models.CharField(max_length=255)
    difficulty = models.PositiveIntegerField(null=True, blank=True,
        help_text="on a scale of: 1-10")
    description = models.TextField()
    tags = tagging.TagField()

    class Meta:
        ordering = ["parent__id"]

    def __unicode__(self):
        if self.parent:
            return "%s > %s" % (self.parent, self.name)
        else:
            return self.name

class QuizModule(models.Model):
    quiz = models.ForeignKey(Quiz)
    module = models.ForeignKey(Module)
    order = models.IntegerField(blank=True, null=True,
        help_text="The order that this module should appear while test")
    randomize = models.BooleanField(help_text="Randomize the appearance of questions in this module")
    num_random_questions = models.IntegerField(blank=True, null=True,
        help_text="If the quiz is randomized, "
        "use this field to set how many questions users must answer or "
        "leave blank to use all questions.")

    class Meta:
        ordering = ["order"]

    def __unicode__(self):
        return u"%s-%s" % (self.quiz, self.module)

class Question(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField()
    difficulty = models.PositiveIntegerField(
        null=True, blank=True, help_text="on a scale of: 1-10")
    point_value = models.IntegerField(default=1)
    module = models.ForeignKey(Module)

    def __unicode__(self):
        return "%s > %s" % (self.module, self.title or self.id)

    def get_answers(self):

        answers = self.possibleanswer_set.all()
        if answers.count() > MAX_CHOICES:
            retval = list(answers.filter(percent_correct__gt=0)[:MAX_CHOICES])
            incorrect = list(answers.filter(percent_correct__lte=0))
            remaining = MAX_CHOICES - len(retval)
            if remaining > 0:
                retval += random.sample(incorrect, remaining)
        else:
            retval = list(answers)
        random.shuffle(retval)
        return retval

    def correct(self, answer):
        possible = self.possibleanswer_set.all()
        count = possible.count()
        if count == 0:
            # opinion/grade later
            return self.point_value, answer
        elif count == 1:
            # short answer
            correct = list(possible)[0]
            if answer == correct.content:
                return self.point_value, answer
        else:
            # multiple guess
            answer = possible.get(id=answer)
            return answer.percent_correct * self.point_value, answer.content

#class MultipleChoiceQuestion(Question):
#
#    def correct(self, answer):
#        return self.possibleanswer_set.filter()
#
#class ShortAnswerQuestion(Question):
#
#    def correct(self, answer):
#        correct = self.possibleanswer_set.get()

class PossibleAnswer(models.Model):

    class Meta:
        ordering = ("id", )

    question = models.ForeignKey(Question)
    content = models.CharField(max_length=255)
    percent_correct = models.FloatField(default=0,
        help_text="Percentage of this questions points that using this answer will reward (-1.0 = -100%; 1.0 = 100%)")
    #explaination = models.TextField()

    def __unicode__(self):
        if self.percent_correct >= 1:
            retval = "Correct Answer"
        elif self.percent_correct > 0:
            retval = "Partially Correct Answer"
        elif self.percent_correct == 0:
            retval = "Incorrect Answer"
        else:
            retval = "Wickedly Placed Incorrect Answer"
        return "%s > %s" % (self.question, retval)

class HelpNote(models.Model):
    question = models.ForeignKey(Question, blank=True, null=True)
    attempt = models.IntegerField()
    content = models.TextField()

class UserNote(models.Model):
    user = models.ForeignKey("auth.User")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    question = models.ForeignKey(Question, blank=True, null=True)
    content = models.TextField()
    private = models.BooleanField(default=False,
        help_text="Notes to help you (and others) understand the answer to this question")

class UserNoteVote(models.Model):
    question = models.ForeignKey(Question)
    note = models.TextField()

class QuizSession(models.Model):
    user = models.ForeignKey("auth.User", blank=True, null=True)
    ip_address = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=255)
    quiz = models.ForeignKey(Quiz)
    started_on = models.DateTimeField(auto_now_add=True)
    ended_on = models.DateTimeField(editable=False, null=True)
    total_score = models.IntegerField(null=True)
    attempt = models.IntegerField(null=True)

    def answered(self):
        return self.useranswer_set.filter(answered_on__isnull=False).order_by("answered_on")

class UserAnswer(models.Model):

    class Meta:
        ordering = ("id",)
        
    session = models.ForeignKey(QuizSession)
    question = models.ForeignKey(Question)
    answer = models.CharField(max_length=256, null=True)
    score = models.IntegerField(null=True)
    answered_on = models.DateTimeField(null=True)

    def save(self):
        created = False
        if not self.id:
            created = True
        super(UserAnswer, self).save()
        if created:
            for possible in self.question.get_answers():
                UserPossibleAnswer(useranswer=self, possibleanswer=possible).save()

    def get_correct_answers(self):
        return PossibleAnswer.objects.filter(userpossibleanswer__useranswer=self, percent_correct__gt=0).order_by("-percent_correct")

class UserPossibleAnswer(models.Model):
    useranswer = models.ForeignKey(UserAnswer)
    possibleanswer = models.ForeignKey(PossibleAnswer)

class UserLongAnswer(UserAnswer):
    content = models.TextField()
