import os.path
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from user.models import Follow
from user.serializers import UserDetailSerializer

USER_URL = reverse("user:users-list")


def test_image_user():
    with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
        img = Image.new("RGB", (10, 10), color=(50, 50, 50))
        img.save(ntf, format="JPEG")
        ntf.seek(0)
        return SimpleUploadedFile(f"test_image.jpg", ntf.read(), content_type="image/jpeg")


class UnauthenticatedUserTest(TestCase):
    def test_get_list_users_no_auth(self):
        response = self.client.get(USER_URL)
        print(response)
        self.assertEqual(response.status_code, 400)

    def test_create_user_no_auth(self):
        user_data = {
            "email": "develop@mail.com",
            "username": "developer",
            "password": "passWORD",
        }
        response = self.client.post(USER_URL, user_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(get_user_model().objects.count(), 1)


class AuthenticatedUserTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user_1 = get_user_model().objects.create_user(
            email="auth_user@mail.com",
            username="auth_user",
            first_name="John",
            last_name="Doe",
            country="USA"
        )
        self.user_1.set_password("PASSWORD321")
        self.user_1.save()

        self.user_2 = get_user_model().objects.create_user(
            email="user_dev@mail.com",
            username="user_dev",
            first_name="Jane",
            last_name="Smith",
            country="Canada"
        )
        self.user_2.set_password("PASSWORD456")
        self.user_2.save()

        self.user_3 = get_user_model().objects.create_user(
            email="best_email@mail.com",
            username="best_name",
            first_name="Best",
            last_name="User",
            country="UK"
        )
        self.user_3.set_password("PASSword321")
        self.user_3.save()

        # Force authentication for user_1
        self.client.force_authenticate(user=self.user_1)

    def test_filter_by_username(self):
        """Test filtering users by username"""
        response = self.client.get(reverse("user:users-list") + "?username=auth_user")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {user["id"] for user in response.data}
        self.assertIn(self.user_1.id, returned_ids)
        self.assertNotIn(self.user_2.id, returned_ids)
        self.assertNotIn(self.user_3.id, returned_ids)

    def test_filter_by_first_name(self):
        """Test filtering users by first name"""
        response = self.client.get(reverse("user:users-list") + "?first_name=John")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {user["id"] for user in response.data}
        self.assertIn(self.user_1.id, returned_ids)
        self.assertNotIn(self.user_2.id, returned_ids)
        self.assertNotIn(self.user_3.id, returned_ids)

    def test_filter_by_last_name(self):
        """Test filtering users by last name"""
        response = self.client.get(reverse("user:users-list") + "?last_name=Doe")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {user["id"] for user in response.data}
        self.assertIn(self.user_1.id, returned_ids)
        self.assertNotIn(self.user_2.id, returned_ids)
        self.assertNotIn(self.user_3.id, returned_ids)

    def test_filter_by_email(self):
        """Test filtering users by email"""
        response = self.client.get(reverse("user:users-list") + "?email=auth_user@mail.com")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {user["id"] for user in response.data}
        self.assertIn(self.user_1.id, returned_ids)
        self.assertNotIn(self.user_2.id, returned_ids)
        self.assertNotIn(self.user_3.id, returned_ids)

    def test_filter_by_country(self):
        """Test filtering users by country"""
        response = self.client.get(reverse("user:users-list") + "?country=USA")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {user["id"] for user in response.data}
        self.assertIn(self.user_1.id, returned_ids)
        self.assertNotIn(self.user_2.id, returned_ids)
        self.assertNotIn(self.user_3.id, returned_ids)

    def test_filter_by_multiple_parameters(self):
        """Test filtering users by multiple parameters"""
        response = self.client.get(reverse("user:users-list") + "?username=best_name&country=UK")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {user["id"] for user in response.data}
        self.assertIn(self.user_3.id, returned_ids)
        self.assertNotIn(self.user_1.id, returned_ids)
        self.assertNotIn(self.user_2.id, returned_ids)

    def test_retrieve_user(self):
        response = self.client.get(reverse("user:users-detail", args=[self.user_1.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.user_1.id)
        self.assertEqual(response.data["email"], self.user_1.email)

    def test_update_user(self):
        user_data = {
            "email": "update_email@mail.com",
            "username": "update_name",
        }
        response = self.client.put(reverse("user:users-detail", args=[self.user_1.id]), user_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], "update_email@mail.com")
        self.assertEqual(response.data["username"], "update_name")

    def test_set_image_on_existing_user(self):
        """Test uploading an image to user"""
        url = reverse("user:users-detail", args=[self.user_1.id])
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.patch(url, {"image": ntf}, format='multipart')

        self.assertEqual(res.status_code, 200)
        self.assertIn("image", res.data)

    def test_action_follow_success(self):
        response = self.client.post(reverse("user:users-follow", args=[self.user_2.id]))

        self.assertEqual(response.status_code, 201)
        print(response.data["success"], "You are now following user_dev.")

    def test_action_follow_myself(self):
        response = self.client.post(reverse("user:users-follow", args=[self.user_1.id]))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "You cannot follow yourself.")

    def test_action_follow_existing_follows(self):
        Follow.objects.create(follower=self.user_1, following=self.user_2)

        response = self.client.post(reverse("user:users-follow", args=[self.user_2.id]))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "You are already following this user.")

    def test_action_unfollow_success(self):
        Follow.objects.create(follower=self.user_1, following=self.user_2)

        response = self.client.post(reverse("user:users-unfollow", args=[self.user_2.id]))

        self.assertEqual(response.status_code, 204)

    def test_action_unfollow_myself(self):
        response = self.client.post(reverse("user:users-unfollow", args=[self.user_1.id]))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "You cannot unfollow yourself.")

    def test_action_unfollow_existing_unfollows(self):
        response = self.client.post(reverse("user:users-unfollow", args=[self.user_2.id]))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "You are not following this user.")

    def test_action_followers(self):
        Follow.objects.create(follower=self.user_2, following=self.user_1)
        Follow.objects.create(follower=self.user_3, following=self.user_1)

        response = self.client.get(reverse("user:users-followers", args=[self.user_1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["followers"]), 2)

    def test_action_following(self):
        Follow.objects.create(follower=self.user_1, following=self.user_3)
        response = self.client.get(reverse("user:users-following", args=[self.user_1.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["following"]), 1)

    def test_action_me(self):
        Follow.objects.create(follower=self.user_1, following=self.user_2)
        Follow.objects.create(follower=self.user_1, following=self.user_3)

        Follow.objects.create(follower=self.user_2, following=self.user_1)

        response = self.client.get(reverse("user:users-me"))

        serializer = UserDetailSerializer(self.user_1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)

        self.assertEqual(len(response.data["following"]), 2)
        self.assertEqual(len(response.data["followers"]), 1)
