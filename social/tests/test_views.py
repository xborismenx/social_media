import tempfile
from datetime import timedelta

from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient

from social.models import Tags, Post, Likes
from social.serializers import PostDetailSerializer

from user.models import Follow

POST_URL = reverse("social:posts-list")


class UnauthenticatedPostTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_post_list_with_unauthentication(self):
        response = self.client.get(POST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AuthenticatedPostTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@mail.com",
            username="test",
        )
        self.client.force_authenticate(user=self.user)

        self.user_2 = get_user_model().objects.create_user(
            email="user_1@mail.com",
            username="user_1",
        )

        self.tag = Tags.objects.create(name="python")
        self.tag_1 = Tags.objects.create(name="django")

        self.post_1 = Post.objects.create(
            text="test",
            owner=self.user,
            date_posted=timezone.now()
        )
        self.post_1.tags.add(self.tag)

        self.post_2 = Post.objects.create(
            text="test_1",
            owner=self.user_2,
            date_posted=timezone.now()
        )


        Follow.objects.create(follower=self.user, following=self.user_2)

    def test_create_post(self):
        post_data = {
            "text": "new test post",
            "tags": [self.tag],
            "date_posted": timezone.now(),
        }
        response = self.client.post(POST_URL, post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 3)

    def test_retrieve_post(self):
        response = self.client.get(reverse("social:posts-detail", args=[self.post_1.id]))

        self.post_1.is_liked = False
        serializer = PostDetailSerializer(self.post_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_by_text(self):
        response = self.client.get(reverse("social:posts-list") + "?text=test")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {post["id"] for post in response.data}
        self.assertIn(self.post_1.id, returned_ids)

    def test_filter_by_tags(self):
        response = self.client.get(reverse("social:posts-list") + f"?tags={self.tag.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {post["id"] for post in response.data}
        self.assertIn(self.post_1.id, returned_ids)

    def test_filter_by_date_lt(self):
        date_lt = (timezone.now() + timedelta(days=1)).strftime('%d.%m.%Y')
        response = self.client.get(reverse("social:posts-list") + f"?date_lt={date_lt}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {post["id"] for post in response.data}
        self.assertIn(self.post_1.id, returned_ids)

    def create_test_two_images(self):
        images = []
        for i in range(2):
            with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
                img = Image.new("RGB", (10, 10), color=(i * 50, i * 50, i * 50))
                img.save(ntf, format="JPEG")
                ntf.seek(0)
                images.append(SimpleUploadedFile(f"test_image_{i}.jpg", ntf.read(), content_type="image/jpeg"))
        return images

    def test_create_post_with_images(self):
        images = self.create_test_two_images()

        post_data = {
            "text": "New post with images",
            "tags": [self.tag],
        }

        post_data.update({f"images_{i}": img for i, img in enumerate(images)})

        response = self.client.post(reverse("social:posts-list"), data=post_data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_post = Post.objects.get(id=response.data["id"])

        self.assertEqual(new_post.images.count(), len(images))

    def test_action_like(self):
        response = self.client.post(reverse("social:posts-like", args=[self.post_1.id]))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "post liked")
        self.assertTrue(Likes.objects.get(user=self.user, post=self.post_1))

    def test_action_unlike(self):
        Likes.objects.create(user=self.user, post=self.post_1)
        response = self.client.post(reverse("social:posts-unlike", args=[self.post_1.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_action_subscribed_posts(self):
        response = self.client.get(reverse("social:posts-subscribed-posts"))
        self.assertEqual(len(response.data), 1)

        self.assertEqual(response.data[0]["id"], self.post_2.id)

    def test_action_my_posts(self):
        post_data = {
            "text": "my_post",
            "owner": self.user,
            "date_posted": timezone.now(),
            "tags": [self.tag_1],

        }
        response_get = self.client.get(reverse("social:posts-my-posts"))
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)

        response_post = self.client.post(reverse("social:posts-my-posts"), data=post_data)
        self.assertEqual(response_post.status_code, status.HTTP_201_CREATED)

        self.assertEqual(len(response_post.data), 2)


    def test_action_liked_posts(self):
        Likes.objects.create(user=self.user, post=self.post_2)

        response = self.client.get(reverse("social:posts-liked-posts"))
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.post_2.id)

    def test_action_comment_with_comment_text(self):
        url = reverse("social:posts-comment", args=[self.post_1.id])

        comment_data = {"comment": "test comment"}
        response = self.client.post(url, data=comment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_action_comment_without_text(self):
        url = reverse("social:posts-comment", args=[self.post_1.id])

        comment_data = {"comment": ""}
        response = self.client.post(url, data=comment_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Comment text is required.")
