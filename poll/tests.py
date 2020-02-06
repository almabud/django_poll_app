import datetime
from django.test import TestCase
from django.utils import timezone
from poll.models import Question
from django.urls import reverse


def create_question(self, question_text, days):
    """
    Creating questions with given question_text. Published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


class QuestionIndexViewTest(TestCase):

    def test_no_questions(self):
        """
        If no question is exist then appropriate message is shown.
        """
        response = self.client.get(reverse('poll:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
         Questions with a pub_date in the past are displayed on the
         index page.
        """
        create_question(self, question_text="Past Question", days=-30)
        response = self.client.get(reverse('poll:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past Question>'])

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(self, question_text="Future Question", days=30)
        response = self.client.get(reverse('poll:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_and_past_question(self):
        """
        If future and past question is available then only display the past question
        """
        create_question(self, question_text="Past Question", days=-30)
        create_question(self, question_text="Future Question", days=30)
        response = self.client.get(reverse('poll:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past Question>'])

    def test_past_two_question(self):
        """Index page may showed multiple question"""
        create_question(self, question_text="Past Question1.", days=-30)
        create_question(self, question_text="Past Question2.", days=-5)
        response = self.client.get(reverse('poll:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'],
                                 ['<Question: Past Question2.>', '<Question: Past Question1.>'])


class QuestionDetailViewTest(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(self, question_text='Future question.', days=5)
        url = reverse('poll:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(self, question_text='Past Question.', days=-5)
        url = reverse('poll:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
