from django.contrib import admin

from social.models import Post, Likes, PostImage


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
    list_display = ("text",)
    inlines = [LikesInline, ImagesPostInline]


admin.site.register(Likes)
