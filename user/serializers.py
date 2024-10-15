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


class UserDetailSerializer(serializers.ModelSerializer):
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
            "password": {"write_only": True, "required": False, "style": {"input_type": "password"}},
            "date_joined": {"read_only": True},
        }

    def update(self, instance, validated_data):
        user = self.context['request'].user

        if user.pk != instance.pk:
            raise serializers.ValidationError({"authorize": "You don't have permission for this user."})

        password = validated_data.get("password")
        if password:
            user.set_password(password)

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)

        instance.save()

        return instance
