from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Article, Publisher

# Create your tests here.
User = get_user_model()

class NewsAppAPITests(APITestCase):

    def setUp(self):
        #create users
        self.journalist = User.objects.create_user(
            username="journalist_user",
            password="password123",
            role="journalist"
        )
        self.editor = User.objects.create_user(
            username="editor_user", password="password123", role="editor"
        )
        self.reader = User.objects.create_user(
            username="reader_user", password="password123", role="reader"
        )

        #create publisher
        self.publisher = Publisher.objects.create(name="Tech Times")
        self.publisher.editors.add(self.editor)
        self.publisher.journalists.add(self.journalist)

        #create articles
        self.approved_article = Article.objects.create(
            title="Approved News",
            content="Content",
            author=self.journalist,
            publisher=self.publisher,
            approved=True,
        )
        self.unapproved_article = Article.objects.create(
            title="Draft News",
            content="Draft Content",
            author=self.journalist,
            approved=False,
        )

    def test_journalist_can_create_article(self):
        self.client.force_authenticate(user=self.journalist)
        url = reverse("article-list")
        data = {
            "title": "New Tech", 
            "content": "Tech content",
            "publisher": self.publisher.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_reader_cannot_create_article(self):
        self.client.force_authenticate(user=self.reader)
        url = reverse("article-list")
        data = {
            "title": "Unauthorized Article", 
            "content": "Reader trying to write content",
            "publisher": self.publisher.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_editor_can_approve_article_and_trigger_signal(self):
        self.client.force_authenticate(user=self.editor)
        url = reverse(
            "article-approve", kwargs={"pk": self.unapproved_article.pk}
        )
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.unapproved_article.refresh_from_db()
        self.assertTrue(self.unapproved_article.approved)

    def test_reader_can_only_get_subscribed_content(self):
        self.reader.subscribed_publishers.add(self.publisher)
        self.client.force_authenticate(user=self.reader)

        url = reverse("article-subscribed")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Approved News")
