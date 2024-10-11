from rest_framework import serializers

from social.models import Post


class PostSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Post
        fields = ("id", "text", "image", "owner")

    def create(self, validated_data):
        request = self.context.get("request")
        post = Post.objects.create(owner=request.user, **validated_data)
        return post
