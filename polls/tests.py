"""Automated tests"""

import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Question

def create_question(question_text, days):
    """Create a question with given 'question_text' and publish the given
    number of 'days' offset to now (negative for questions published in the
    past, positive for questions yet to be published)"""
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionDetailViewTests(TestCase):
    """test cases for the DetailView generic view"""

    def test_future_question(self):
        """the detail view of a question with a future pub_date returns a 404"""
        future_question = create_question(question_text='Future question',days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """detail view of a question with a past pub_date displays question text"""

        past_question = create_question(question_text='Past question', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

class QuestionIndexViewTests(TestCase):
    """test cases for the IndexView of questions"""

    def test_no_questions(self):
        """if no questions exist, appropriate message is displyed"""
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question(self):
        """questions with future pub_dates aren't displayed on index page"""
        create_question(question_text='Future question', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """if past and future questions exist, only past questions display"""
        create_question(question_text='Past question', days=-30)
        create_question(question_text='Future question', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question>']
        )

    def test_two_past_questions(self):
        """questions index page may display multiple questions"""
        create_question(question_text='Past question 1', days=-30)
        create_question(question_text='Past question 2', days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2>', '<Question: Past question 1>']
        )

class QuestionModelTests(TestCase):
    """test cases for the Question model"""

    def test_was_published_recentyly_with_future_question(self):
        """was_published_recently() returns False for questions whose pub_date
        is in the future"""
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)

        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """was_published_recently() returns False for questions whose pub_date
        is older than 1 day"""
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """was_published_recently() returns True for questions whose pub_date
        is within the last day"""
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59,
            seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)
