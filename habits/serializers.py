from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import ValidationError
from habits.models import Habit
from habits.validators import (
    RewardAndRelatedHabitValidator,
    NiceHabitValidator,
    RelatedHabitIsNiceValidator,
    ExecutionTimeValidator,
    PeriodicityValidator,
)


class HabitSerializer(ModelSerializer):
    class Meta:
        model = Habit
        fields = "__all__"
        validators = [
            RewardAndRelatedHabitValidator(),
            NiceHabitValidator(),
        ]

    def validate(self, data):
        # Получаем текущий объект (для PATCH) или None (для POST)
        instance = getattr(self, "instance", None)

        # Проверка только для полезных привычек
        if not data.get(
            "nice_habit", False if instance is None else instance.nice_habit
        ):
            # Используем новые значения или текущие (если они не переданы в PATCH)
            reward = data.get("reward", None if instance is None else instance.reward)
            related_habit = data.get(
                "related_habit", None if instance is None else instance.related_habit
            )

            # Проверяем, что хотя бы одно поле заполнено
            if not reward and not related_habit:
                raise ValidationError(
                    "Для полезной привычки укажите либо вознаграждение, "
                    "либо связанную приятную привычку"
                )

        # Проверка связанной привычки
        if "related_habit" in data and data["related_habit"]:
            try:
                related_habit = Habit.objects.get(pk=data["related_habit"])
                RelatedHabitIsNiceValidator()(related_habit)
            except Habit.DoesNotExist:
                raise ValidationError("Связанная привычка не найдена")

        # Валидация числовых полей
        if "execution_time" in data:
            ExecutionTimeValidator()(data["execution_time"])

        if "periodicity" in data:
            PeriodicityValidator()(data["periodicity"])

        return data
