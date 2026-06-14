from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from tracker.models import User, Category

class AuthTests(APITestCase):

    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('token_obtain_pair')
        self.profile_url = reverse('profile')

        self.valid_payload = {
            'email': 'juan@example.com',
            'first_name': 'Juan',
            'last_name': 'dela Cruz',
            'password': 'Str0ngPass!',
            'confirm_password': 'Str0ngPass!',
        }

    def test_register_success(self):
        response = self.client.post(self.register_url, self.valid_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], 'juan@example.com')
        self.assertNotIn('password', response.data)
        self.assertTrue(User.objects.filter(email='juan@example.com').exists())

    def test_register_creates_default_categories(self):
        self.client.post(self.register_url, self.valid_payload)

        user = User.objects.get(email='juan@example.com')
        categories = Category.objects.filter(user=user)

        self.assertTrue(categories.exists())
        self.assertGreater(categories.count(), 0)

    def test_register_duplicate_email_fails(self):
        self.client.post(self.register_url, self.valid_payload)

        # try registering again with the same email
        response = self.client.post(self.register_url, self.valid_payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_register_password_mismatch_fails(self):
        payload = self.valid_payload.copy()
        payload['confirm_password'] = 'DifferentPass!'

        response = self.client.post(self.register_url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_register_weak_password_fails(self):
        payload = self.valid_payload.copy()
        payload['email'] = 'weak@example.com'
        payload['password'] = '123'
        payload['confirm_password'] = '123'

        response = self.client.post(self.register_url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_login_success(self):
        self.client.post(self.register_url, self.valid_payload)

        response = self.client.post(self.login_url, {
            'email': 'juan@example.com',
            'password': 'Str0ngPass!',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_wrong_password_fails(self):
        self.client.post(self.register_url, self.valid_payload)

        response = self.client.post(self.login_url, {
            'email': 'juan@example.com',
            'password': 'WrongPassword!',
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_requires_authentication(self):
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_returns_current_user(self):
        self.client.post(self.register_url, self.valid_payload)

        login_response = self.client.post(self.login_url, {
            'email': 'juan@example.com',
            'password': 'Str0ngPass!',
        })
        access_token = login_response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'juan@example.com')

    def test_profile_partial_update(self):
        self.client.post(self.register_url, self.valid_payload)

        login_response = self.client.post(self.login_url, {
            'email': 'juan@example.com',
            'password': 'Str0ngPass!',
        })
        access_token = login_response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.patch(self.profile_url, {'first_name': 'Carlo'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Carlo')