from django.db import models
from django.db.models.signals import post_save
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
    name = models.CharField(max_length=255)
    difficulty = models.PositiveIntegerField(null=True, blank=True,
        help_text="on a scale of: 1-10")
    description = models.TextField(blank=True)
    allow_practice = models.BooleanField(default=True)
    tags = tagging.TagField()

    class Meta:
        ordering = ["name"]

    def __unicode__(self):
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

    def get_questions(self):
        questions = self.module.question_set.all()
        if self.randomize and self.num_random_questions < questions.count():

            retval = random.sample(questions, self.num_random_questions)
        else:
            retval = list(questions)
        random.shuffle(retval)
        return retval

class Question(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField()
    difficulty = models.PositiveIntegerField(
        null=True, blank=True, help_text="on a scale of: 1-10")
    point_value = models.IntegerField(default=1)
    module = models.ForeignKey(Module)
    module_answers = models.BooleanField(default=False,
        help_text="Use correct answers for other questions in this module "
        "to generate incorrect answers for this question")

    def __unicode__(self):
        return "%s > %s" % (self.module, self.title or self.id)

    def get_module_answers(self):
        """ get an answer list with answers from the same module """

        # first get all of the question's answers
        retval = list(self.possibleanswer_set.all())

        if len(retval) < MAX_CHOICES:
            retval += PossibleAnswer.objects.filter(
                question__module=self.module, percent_correct__gt=0
            ).exclude(content__in=[pa.content for pa in retval])[:MAX_CHOICES - len(retval)]

        random.shuffle(retval)
        return retval

    def get_answers(self):

        if self.module_answers:
            return self.get_module_answers()
        else:
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

    def correct(self, answer_id):
        answered = self.possibleanswer_set.filter(userpossibleanswer__id=answer_id)
        if answered.question == self:
            return answer.percent_correct * self.point_value
        else:
            return 0 # no points if this

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
    explaination = models.TextField(blank=True, null=True,
        help_text="an explaination why this answer is or isn't true")

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

class UserNote(models.Model):
    user = models.ForeignKey("auth.User")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    question = models.ForeignKey(Question, blank=True, null=True)
    content = models.TextField()
    private = models.BooleanField(default=False,
        help_text="Notes to help you (and others) understand the answer to this question")
    score = models.IntegerField(default=0, editable=False)

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
    practice = models.BooleanField(default=False)

    def answered(self):
        return self.useranswer_set.filter(answered_on__isnull=False).order_by("answered_on")

class UserAnswer(models.Model):
    """ response given by a user """

    class Meta:
        ordering = ("id",)
        
    session = models.ForeignKey(QuizSession)
    question = models.ForeignKey(Question)
    answer = models.CharField(max_length=256, null=True)
    score = models.IntegerField(null=True)
    answered_on = models.DateTimeField(null=True)
    attempt = models.IntegerField(default=1)

    def get_correct_answers(self):
        return PossibleAnswer.objects.filter(userpossibleanswer__useranswer=self, percent_correct__gt=0).order_by("-percent_correct")

def create_answer_set(sender, instance, created, **kwargs):
        if created:
            for possible in instance.question.get_answers():
                UserPossibleAnswer(useranswer=instance,
                    possibleanswer=possible).save()

post_save.connect(create_answer_set, sender=UserAnswer)

class UserPossibleAnswer(models.Model):
    """ precached options for a user to try, created when a useranswer is saved """
    useranswer = models.ForeignKey(UserAnswer)
    possibleanswer = models.ForeignKey(PossibleAnswer)
    point_value = models.IntegerField()
    chosen = models.BooleanField(default=False)

    def save(self):
        if self.possibleanswer.question != self.useranswer.question:
            self.point_value = 0
        else:
            self.point_value = self.possibleanswer.question.point_value * \
                self.possibleanswer.percent_correct
        super(UserPossibleAnswer, self).save()