from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    url(r'^(\w+)/', quiz_start, name="quiz-view"),
#    url(r'^/$', quiz_index, name="quiz-index"),
)
