from rest_framework.exceptions import ValidationError


class RewardAndRelatedHabitValidator:
    def __call__(self, data):
        if isinstance(data, dict):
            reward = data.get("reward")
            related_habit = data.get("related_habit")
        else:
            reward = data.reward
            related_habit = data.related_habit

        if reward and related_habit:
            raise ValidationError(
                "Нельзя указывать одновременно вознаграждение и связанную привычку"
            )


class NiceHabitValidator:
    def __call__(self, data):
        if isinstance(data, dict):
            nice_habit = data.get("nice_habit", False)
            reward = data.get("reward")
            related_habit = data.get("related_habit")
        else:
            nice_habit = data.nice_habit
            reward = data.reward
            related_habit = data.related_habit

        if nice_habit:
            if reward:
                raise ValidationError("Приятная привычка не может иметь награду")
            if related_habit:
                raise ValidationError("Приятная привычка не может быть связанной")


class RelatedHabitIsNiceValidator:
    def __call__(self, data):
        if isinstance(data, dict):
            related_habit = data.get("related_habit")
        else:
            related_habit = data.related_habit

        if related_habit:
            if not related_habit.nice_habit:
                raise ValidationError("Связанная привычка должна быть приятной")


class ExecutionTimeValidator:
    def __call__(self, execution_time):
        if execution_time > 120:
            raise ValidationError("Время выполнения не должно превышать 120 секунд.")


class PeriodicityValidator:
    def __call__(self, periodicity):
        if periodicity < 1:
            raise ValidationError(
                "Привычка должна выполняться хотя бы 1 раз в день. "
                "Укажите значение от 1 до 7."
            )
        if periodicity > 7:
            raise ValidationError(
                "Привычка не может выполняться реже чем 1 раз в 7 дней. "
                "Максимальная периодичность - 7 дней."
            )
