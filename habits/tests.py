from datetime import time
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from habits.models import Habit
from habits.validators import (
    RewardAndRelatedHabitValidator,
    NiceHabitValidator,
    RelatedHabitIsNiceValidator,
    ExecutionTimeValidator,
    PeriodicityValidator,
)
from users.models import User


class HabitValidatorsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email="testuser@example.com", first_name="Test", last_name="User"
        )

        self.nice_habit = Habit.objects.create(
            user=self.user,
            place="Дом",
            time=time(8, 0),
            action="пить кофе",
            nice_habit=True,
            execution_time=120,
            periodicity=1,
        )

        self.regular_habit = Habit.objects.create(
            user=self.user,
            place="Спортзал",
            time=time(19, 0),
            action="делать зарядку",
            nice_habit=False,
            execution_time=90,
            periodicity=2,
        )

    def test_reward_and_related_habit_validator(self):
        """Тест валидации одновременного указания награды и связанной привычки."""
        validator = RewardAndRelatedHabitValidator()
        data = {"reward": "шоколадка", "related_habit": self.nice_habit.id}

        with self.assertRaises(ValidationError) as context:
            validator(data)

        self.assertEqual(
            str(context.exception.detail[0]),
            "Нельзя указывать одновременно вознаграждение и связанную привычку",
        )

    def test_nice_habit_validator_with_reward(self):
        """Тест валидации приятной привычки с наградой"""
        validator = NiceHabitValidator()
        data = {"nice_habit": True, "reward": "чай"}

        with self.assertRaises(ValidationError) as context:
            validator(data)

        self.assertEqual(
            str(context.exception.detail[0]), "Приятная привычка не может иметь награду"
        )

    def test_nice_habit_validator_with_related_habit(self):
        """Тест валидации приятной привычки со связанной привычкой"""
        validator = NiceHabitValidator()
        data = {"nice_habit": True, "related_habit": self.regular_habit.id}

        with self.assertRaises(ValidationError) as context:
            validator(data)

        self.assertEqual(
            str(context.exception.detail[0]),
            "Приятная привычка не может быть связанной",
        )

    def test_related_habit_is_nice_validator(self):
        """Тест валидации что связанная привычка является приятной"""
        validator = RelatedHabitIsNiceValidator()
        data = {"related_habit": self.regular_habit}

        with self.assertRaises(ValidationError) as context:
            validator(data)

        self.assertEqual(
            str(context.exception.detail[0]), "Связанная привычка должна быть приятной"
        )

    def test_execution_time_validator(self):
        """Тест валидации времени выполнения привычки"""
        validator = ExecutionTimeValidator()

        with self.assertRaises(ValidationError) as context:
            validator(121)

        self.assertEqual(
            str(context.exception.detail[0]),
            "Время выполнения не должно превышать 120 секунд.",
        )

    def test_periodicity_validator_too_small(self):
        """Тест валидации слишком маленькой периодичности"""
        validator = PeriodicityValidator()

        with self.assertRaises(ValidationError) as context:
            validator(0)

        self.assertEqual(
            str(context.exception.detail[0]),
            "Привычка должна выполняться хотя бы 1 раз в день. Укажите значение от 1 до 7.",
        )

    def test_periodicity_validator_too_large(self):
        """Тест валидации слишком большой периодичности"""
        validator = PeriodicityValidator()

        with self.assertRaises(ValidationError) as context:
            validator(8)

        self.assertEqual(
            str(context.exception.detail[0]),
            "Привычка не может выполняться реже чем 1 раз в 7 дней. Максимальная периодичность - 7 дней.",
        )

    def test_valid_habit_passes_all_validations(self):
        """Тест что корректная привычка проходит все валидации"""
        # Тест для полезной привычки с наградой
        data_with_reward = {
            "user": self.user.id,
            "place": "Балкон",
            "time": "07:30:00",
            "action": "дышать свежим воздухом",
            "nice_habit": False,
            "reward": "кофе",
            "execution_time": 60,
            "periodicity": 1,
        }

        # Тест для полезной привычки со связанной привычкой
        data_with_related = {
            "user": self.user.id,
            "place": "Балкон",
            "time": "07:30:00",
            "action": "дышать свежим воздухом",
            "nice_habit": False,
            "related_habit": self.nice_habit.id,
            "execution_time": 60,
            "periodicity": 1,
        }

        RewardAndRelatedHabitValidator()(data_with_reward)
        NiceHabitValidator()(data_with_reward)
        ExecutionTimeValidator()(data_with_reward["execution_time"])
        PeriodicityValidator()(data_with_reward["periodicity"])

        RewardAndRelatedHabitValidator()(data_with_related)
        NiceHabitValidator()(data_with_related)
        RelatedHabitIsNiceValidator()({"related_habit": self.nice_habit})
        ExecutionTimeValidator()(data_with_related["execution_time"])
        PeriodicityValidator()(data_with_related["periodicity"])
