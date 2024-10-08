from django.contrib import admin

from social.models import Post, Likes


class LikesInline(admin.TabularInline):
    model = Likes
    fields = ('user', "liked_at",)
    readonly_fields = ('liked_at',)
    extra = 0


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("text", "image",)
    inlines = [LikesInline]


admin.site.register(Likes)
