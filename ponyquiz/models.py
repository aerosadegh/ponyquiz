from django.db import models
from tagging import fields as tagging

# Create your models here.
class Quiz(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
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
    modules = models.ManyToManyField(Module)
    title = models.CharField(max_length=255, blank=True, null=True)
    slug = models.CharField(max_length=255)
    content = models.TextField()

    def correct(self, answer):
        raise NotImplementedError

class MultipleChoiceQuestion(Question):
    class Meta:
        proxy = True

    def correct(self, answer):
        return self.possibleanswer_set.filter()

class PossibleAnswer(models.Model):
    question = models.ForeignKey(Question)
    is_correct = models.BooleanField(help_text="This is a correct answer")
    content = models.CharField(max_length=255)

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
    user = models.ForeignKey("auth.User")
    started_on = models.DateTimeField(auto_now_add=True)
    ended_on = models.DateTimeField(editable=False, null=True)
    total_score = models.IntegerField()
    attempt = models.IntegerField()

class UserAnswer(models.Model):
    user = models.ForeignKey("auth.User")
    answer = models.CharField(max_length=256)
    score = models.IntegerField()

class UserLongAnswer(UserAnswer):
    content = models.TextField()
