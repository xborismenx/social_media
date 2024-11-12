from django.contrib import admin

from social.models import Post, Likes, PostImage, Tags, Comments


class ImagesPostInline(admin.TabularInline):
    model = PostImage
    fields = ("image", "uploaded_at")
    readonly_fields = ("uploaded_at",)


class LikesInline(admin.TabularInline):
    model = Likes
    fields = ('user', "liked_at",)
    readonly_fields = ('liked_at',)
    extra = 0


class CommentsInline(admin.TabularInline):
    model = Comments
    fields = ('user', "comment", "date_posted",)
    readonly_fields = ('date_posted',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("text", "get_tags")
    inlines = [LikesInline, ImagesPostInline, CommentsInline]

    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]


admin.site.register(Comments, admin.ModelAdmin)
admin.site.register(Likes)

@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ("id", "name",)
