import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Question, Choice
# Create your tests here.



class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """ was_publishe_recently() returns False for question whose pub_dat is in future """
        time = timezone.now() + datetime.timedelta(days= 30)
        future_question = Question(pub_date = time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """ was_published_recently return False for question whose pub_date is older than 1 day"""
        time = timezone.now() - datetime.timedelta(days= 1, seconds=1)
        old_question = Question(pub_date  = time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """ was_published_recently() returns True for question whose pub_date is within the last day"""
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date = time)
        self.assertIs(recent_question.was_published_recently(), True)   


def create_question(question_text, days):
    """ 
    Create a question with the given 'question_text' and published the given number of `days` offset to now
    (negative for question published in the past , positve for question that have yet to be published)
    """
    time = timezone.now() + datetime.timedelta(days= days)
    return Question.objects.create(question_text = question_text, pub_date= time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """ if no Question exists the appropriate message is displayed """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are Available")
        self.assertQuerySetEqual(response.content["latest_question_list"], [])

    def test_past_questions(self):
        """ Question with the pub_date in past are displayed"""
        question = create_question(question_text="Past questions" , days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.content["latest_question_list"],
            [question]
        )
    
    def test_future_questions(self):
        """
        Question with the pub_date in the future aren't displayed on the index page.
        """
        create_question(question_text="Future Question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available")
        self.assertQuerySetEqual(
            response.content["latest_question_list"],
            []

        )
    
    def test_future_question_and_past_question(self):
        """ 
        Even if both past and future question exist display only past question
        """
        question = create_question(question_text="Past question", days=-30)
        create_question(question_text="Future Question", days = 30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.content["latest_question_list"],
            [question],
        )

    def test_two_past_questions(self):
        """
        the question index page may display multiple questions.
        """
        question1 = create_question(question_text="Past Question 1", days=-30)
        question2 = create_question(question_text="Past Question 2", days = -5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.content["latest_question_list"],
            [question2, question1]
        )


# test cased for detail view
class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """ The detail view of a question with pub_date in the future returns a 404 not found """
        future_question = create_question(question_text="Future Question.", days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """ 
        The detail view of the question with a pub_date in the past displays the question's text
        """
        past_question = create_question(question_text="Past Question", days=-5)
        url = reverse("polls:detail", args= (past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

# Creating a test for a new create_question_view
class QuestionCreateViewTests(TestCase):
    def setUp(self):
        # creating a user and loging them before every test cases
        self.username = "testuser"
        self.password = "password123"
        self.user = User.objects.create_user(username = self.username, password=self.password)
        self.client.login(username = self.username, password = self.password)
        self.create_url = reverse("polls:question_create")

    def test_create_question_with_choice_succeeds(self):
        # submitting a valid question form and choice formset successfully create the record in the database 
        # and redirect to the index

        form_data = {
            "question_text": "What is the favourite framework",
            "choice_set-TOTAL_FORMS": "3",
            "choice_set-INITIAL_FORMS": "0",
            "choice_set-MIN_NUM_FORMS": "0",
            "choice_set-MAX_NUM_FORMS": "1000",
            
            
            "choice_set-0-choice_text": "Django",
            "choice_set-1-choice_text": "React",
            "choice_set-2-choice_text": "FasetAPI", 
        }
        # simulating hitting the create poll button
        response = self.client.post(self.create_url, data = form_data)
        if response.status_code == 200:
            print("\n!!!FORM ERRORS:", response.context['form'].errors)
            print("!!! FORMSET ERRORS:", response.context['formset'].errors, "\n")
        # check that it is successfully redirected back to the index page (HTTP303)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("polls:index"))

        # Assert the question was saved to the database
        self.assertEqual(Question.objects.count(), 1)
        new_question = Question.objects.first()
        self.assertEqual(new_question.question_text, "What is the favourite framework")
        self.assertEqual(new_question.author, self.user)

        # Assert that all the 3 choices were linked to that question in the database
        self.assertEqual(Choice.objects.count(), 3)
        choices = new_question.choice_set.all()
        self.assertEqual(choices[0].choice_text, "Django")
        self.assertEqual(choices[1].choice_text, "React")
        self.assertEqual(choices[2].choice_text, "FasetAPI")

