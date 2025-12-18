from rest_framework.serializers import ModelSerializer

from users.models import User


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "is_superuser",
            "is_staff",
            "is_active",
            "tg_chat_id",
        ]
