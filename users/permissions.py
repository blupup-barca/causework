from rest_framework import permissions


class HabitPermission(permissions.BasePermission):
    """
    Универсальный permission для привычек:
    - Владелец имеет полный доступ
    - Все пользователи могут читать публичные привычки
    - Остальные действия запрещены
    """

    def has_object_permission(self, request, view, obj):
        # Владелец имеет полный доступ
        if obj.user == request.user:
            return True

        # Чтение разрешено для публичных привычек
        if request.method in permissions.SAFE_METHODS:
            return obj.public_habit

        # Все остальные случаи запрещены
        return False
