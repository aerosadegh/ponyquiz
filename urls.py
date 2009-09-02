from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    url(r'^usernote/add/', add_usernote, name="quiz-user-note"),
    url(r'^session/(\d+)/end/', quiz_end, name="quiz-end"),
    url(r'^session/(\d+)/', quiz_question, name="quiz-question"),
    url(r'^([\w\-]+)/', quiz_intro, name="quiz-intro"),
    url(r'^$', quiz_index, name="quiz-index"),
)
