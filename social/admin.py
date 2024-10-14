from django.contrib import admin

from social.models import Post, Likes, PostImage, Tags


class ImagesPostInline(admin.TabularInline):
    model = PostImage
    fields = ("image", "uploaded_at")
    readonly_fields = ("uploaded_at",)


class LikesInline(admin.TabularInline):
    model = Likes
    fields = ('user', "liked_at",)
    readonly_fields = ('liked_at',)
    extra = 0


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("text", "get_tags")
    inlines = [LikesInline, ImagesPostInline]

    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]


admin.site.register(Likes)
admin.site.register(Tags)
