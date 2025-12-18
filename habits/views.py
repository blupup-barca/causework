from django.db.models import Q
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from habits.models import Habit
from habits.paginations import HabitPagination
from habits.serializers import HabitSerializer
from users.permissions import HabitPermission


class HabitViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с привычками"""

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, HabitPermission]
    pagination_class = HabitPagination

    def get_queryset(self):
        """Возвращает привычки текущего пользователя и публичные привычки"""
        return Habit.objects.filter(
            Q(user=self.request.user) | Q(public_habit=True)
        ).order_by("id")

    def perform_create(self, serializer):
        """Создает привычку, привязывая к текущему пользователю"""
        serializer.save(user=self.request.user)


class PublicHabitListAPIView(ListAPIView):
    """API для получения списка публичных привычек"""

    queryset = Habit.objects.filter(public_habit=True)
    serializer_class = HabitSerializer
    permission_classes = [AllowAny]
    pagination_class = HabitPagination
