from django.utils import timezone

from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("email", "username", "password")
        extra_kwargs = {
            "password": {"write_only": True, "style": {"input_type": "password", "min_length": 6}},
            "username": {"required": True},
        }

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)


class UserListSerializer(serializers.ModelSerializer):
    followers = serializers.IntegerField(source='followers_count', read_only=True)
    following = serializers.IntegerField(source='following_count', read_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "password",
            "username",
            "first_name",
            "last_name",
            "image",
            "city",
            "country",
            "birth_date",
            "followers",
            "following",
            "bio",
            "date_joined",
        )
        extra_kwargs = {
            "password": {"write_only": True, "style": {"input_type": "password"}},
            "date_joined": {"read_only": True},
        }


class UserDetailSerializer(serializers.ModelSerializer):
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "password",
            "username",
            "first_name",
            "last_name",
            "image",
            "city",
            "country",
            "birth_date",
            "followers",
            "following",
            "bio",
            "date_joined",
        )
        extra_kwargs = {
            "password": {"write_only": True, "required": False, "style": {"input_type": "password"}},
            "username": {"required": False},
            "date_joined": {"read_only": True},
        }

    def validate_birth_date(self, value):
        if value >= timezone.now().date():
            raise serializers.ValidationError("Birth date cannot be in the future")
        return value

    def get_followers(self, obj):
        followers = Follow.objects.filter(following=obj)
        return followers.count()

    def get_following(self, obj):
        followings = Follow.objects.filter(follower=obj)
        return followings.count()

    def update(self, instance, validated_data):
        user = self.context['request'].user

        if user.pk != instance.pk:
            raise serializers.ValidationError({"authorize": "You don't have permission for this user."})

        password = validated_data.get("password")
        if password:
            user.set_password(password)

        instance.username = validated_data.get("username", instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.image = validated_data.get('image', instance.image)
        instance.city = validated_data.get('city', instance.city)
        instance.country = validated_data.get('country', instance.country)
        instance.birth_date = validated_data.get('birth_date', instance.birth_date)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.save()

        return instance


class UserFollower(serializers.ModelSerializer):
    followers = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ("email", "followers",)

    def get_followers(self, obj):
        followers = Follow.objects.filter(following=obj)
        return [follower.follower.email for follower in followers]


class UserFollowing(serializers.ModelSerializer):
    following = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ("email", "following",)

    def get_following(self, obj):
        following = Follow.objects.filter(follower=obj)
        return [follow.following.email for follow in following]
