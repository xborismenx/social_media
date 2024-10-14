from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "password",
            "email",
            "first_name",
            "last_name",
            "image",
            "city",
            "country",
            "birth_date",
            "bio",
            "date_joined",
        )
        extra_kwargs = {
            "password": {"write_only": True, "style": {"input_type": "password"}},
            "date_joined": {"read_only": True},
        }

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)
