from rest_framework import serializers

from social.models import Post, Likes, PostImage


class ImagePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ("post", "image", "uploaded_at")


class LikesSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Likes
        fields = ('user', 'liked_at')


class PostSerializer(serializers.ModelSerializer):
    images = ImagePostSerializer(many=True, read_only=True)
    owner = serializers.ReadOnlyField(source="owner.username")
    likes = LikesSerializer(source="post_likes", many=True)

    class Meta:
        model = Post
        fields = ("id", "text", "images", "owner", "likes", "date_posted")

    def create(self, validated_data):
        request = self.context.get("request")
        post = Post.objects.create(owner=request.user, **validated_data)
        return post
