from django.db import models

from config import settings


class Habit(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="создатель привычки",
        help_text="укажите создателя привычки",
    )
    place = models.CharField(
        max_length=255,
        verbose_name="место",
        help_text="укажите место, в котором необходимо выполнять привычку",
    )
    time = models.TimeField(
        verbose_name="время",
        help_text="укажите время, когда необходимо выполнять привычку",
    )
    action = models.CharField(
        max_length=255,
        verbose_name="действие",
        help_text="укажите действие, которое требуется выполнять",
    )
    nice_habit = models.BooleanField(default=False, verbose_name="приятная привычка")
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        verbose_name="связанная привычка",
        null=True,
        blank=True,
        limit_choices_to={"nice_habit": True},
    )

    reward = models.CharField(
        max_length=255,
        verbose_name="вознаграждение",
        help_text="укажите вознаграждение за выполнение привычки",
        blank=True,
        null=True,
    )
    periodicity = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="периодичность выполнения привычки",
        help_text="укажите периодичность выполнения привычки(например, 1 раз в день",
    )
    execution_time = models.PositiveSmallIntegerField(
        verbose_name="время в секундах",
        help_text="укажите сколько времени(в секундах) потребуется на выполнение привычки",
    )
    public_habit = models.BooleanField(
        default=False, verbose_name="признак публичности"
    )

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"

    def __str__(self):
        return f"Я буду{self.action} в {self.time} в {self.place}"
