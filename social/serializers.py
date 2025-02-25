from django.utils import timezone
from rest_framework import serializers

from social.models import Post, Likes, PostImage, Tags, Comments


class ImagePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ("image", "uploaded_at")


class LikesSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Likes
        fields = ('user', 'liked_at')


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ("name",)


class PostListSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    owner = serializers.ReadOnlyField(source="owner.username")
    likes = serializers.SerializerMethodField(source="likes")
    tags = serializers.SlugRelatedField(many=True, queryset=Tags.objects.all(), slug_field="name")
    is_liked = serializers.BooleanField(read_only=True)
    date_posted = serializers.DateTimeField(read_only=True)
    scheduled_time = serializers.DateTimeField(write_only=True, required=False)

    class Meta:
        model = Post
        fields = ("id", "text", "images", "likes", "tags", "is_liked", "date_posted", "owner", "scheduled_time")

    def get_images(self, obj):
        request = self.context.get("request")
        return [request.build_absolute_uri(image.image.url) for image in obj.images.all()]

    def get_likes(self, obj):
        return obj.post_likes.count()


class PostCreateSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(many=True, queryset=Tags.objects.all(), slug_field="name")
    images = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)
    scheduled_time = serializers.DateTimeField(write_only=True, required=False)

    class Meta:
        model = Post
        fields = ("text", "tags", "images", "scheduled_time")

    def create(self, validated_data):
        request = self.context.get("request")
        images_data = validated_data.pop('images', [])
        tags = validated_data.pop('tags', [])
        scheduled_time = validated_data.pop('scheduled_time', None)

        if not scheduled_time:
            validated_data["date_posted"] = timezone.now()

        post = Post.objects.create(owner=request.user, scheduled_time=scheduled_time, **validated_data)

        post.tags.set(tags)

        for image_data in images_data:
            PostImage.objects.create(post=post, image=image_data)

        return post


class CommentsSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Comments
        fields = ("id", "user", "comment", "date_posted")


class CommentsCreateSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    comment = serializers.CharField()

    class Meta:
        model = Comments
        fields = ("id", "user", "comment", "date_posted")


class PostDetailSerializer(serializers.ModelSerializer):
    images = ImagePostSerializer(many=True, read_only=True)
    owner = serializers.ReadOnlyField(source="owner.username")
    tags = serializers.SlugRelatedField(many=True, queryset=Tags.objects.all(), slug_field="name")
    likes = LikesSerializer(source="post_likes", many=True, read_only=True)
    is_liked = serializers.BooleanField()
    comments = CommentsSerializer(source="post_comments", many=True)

    class Meta:
        model = Post
        fields = ("id", "text", "images", "owner", "likes", "date_posted", "tags", "is_liked", "comments")
