import datetime
from django.test import TestCase
from django.utils import timezone
# Create your tests here.

from .models import Question

class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """ was_publishe_recently() returns False for question whose pub_dat is in future """
        time = timezone.now() + datetime.timedelta(days= 30)
        future_question = Question(pub_date = time)
        self.assertIs(future_question.was_published_recently(), False)

        
