from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import User
from habits.models import Habit
from unittest.mock import patch, MagicMock
from habits.services import send_telegram_message


class UserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("users:register")
        self.login_url = reverse("users:login")

    def test_user_registration(self):
        """Тестирование регистрации через API"""
        data = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="test@example.com").exists())

    def test_user_login_success(self):
        """Тестирование успешного входа"""
        user = User.objects.create(
            email="login@example.com", first_name="Login", last_name="User"
        )
        user.set_password("testpass123")
        user.save()

        login_data = {"email": "login@example.com", "password": "testpass123"}
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_login_failure(self):
        """Тестирование неудачного входа"""
        user = User.objects.create(
            email="fail@example.com", first_name="Fail", last_name="User"
        )
        user.set_password("testpass123")
        user.save()

        login_data = {"email": "fail@example.com", "password": "wrongpassword"}
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class HabitPermissionTests(TestCase):
    """Тесты прав доступа к привычкам"""

    def setUp(self):
        self.client = APIClient()

        self.user1 = User.objects.create(
            email="user1@test.com", first_name="User1", last_name="Test"
        )
        self.user1.set_password("testpass123")
        self.user1.save()

        self.user2 = User.objects.create(
            email="user2@test.com", first_name="User2", last_name="Test"
        )
        self.user2.set_password("testpass123")
        self.user2.save()

        self.habit = Habit.objects.create(
            user=self.user1,
            place="Дом",
            time="08:00:00",
            action="Чтение",
            execution_time=120,
            periodicity=1,
            public_habit=False,
        )

        self.habit_detail_url = reverse(
            "habits:habit-detail", kwargs={"pk": self.habit.pk}
        )

    def test_owner_has_access(self):
        """Создатель привычки имеет доступ"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.habit_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_other_user_no_access(self):
        """Другой пользователь не имеет доступа к приватной привычке"""
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.habit_detail_url)

        self.assertIn(
            response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        )

    def test_public_habit_access(self):
        """Публичную привычку может просматривать любой авторизованный пользователь"""
        public_habit = Habit.objects.create(
            user=self.user1,
            place="Парк",
            time="07:00:00",
            action="Пробежка",
            execution_time=60,
            periodicity=1,
            public_habit=True,
        )

        url = f"/habits/{public_habit.pk}/"

        self.client.force_authenticate(user=self.user2)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TelegramServiceTest(TestCase):
    """Тесты для отправки Telegram-сообщений"""

    @classmethod
    def setUpTestData(cls):
        # Создаем тестового пользователя
        cls.user = User.objects.create(email="test@example.com", tg_chat_id="123456")

    @patch("habits.services.requests.post")
    def test_send_telegram_message_correct_params(self, mock_post):
        """Проверяем корректность параметров вызова"""
        # Настраиваем мок
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Вызываем функцию
        test_message = "Тестовое сообщение"
        send_telegram_message(self.user.tg_chat_id, test_message)

        # Проверяем вызов requests.post
        mock_post.assert_called_once()

        # Получаем аргументы вызова
        called_url = mock_post.call_args[0][0]
        called_params = mock_post.call_args[1]["params"]

        # Проверяем URL (без токена)
        self.assertIn("api.telegram.org", called_url)
        self.assertIn("/sendMessage", called_url)

        # Проверяем параметры
        self.assertEqual(called_params["chat_id"], self.user.tg_chat_id)
        self.assertEqual(called_params["text"], test_message)

    @patch("habits.services.requests.post")
    def test_send_telegram_message_with_none_chat_id(self, mock_post):
        """Проверяем поведение при None в chat_id"""
        send_telegram_message(None, "Сообщение")

        mock_post.assert_called_once()
