from django.contrib import admin

from .models import Category, Comment, Review, User, Title, Genre, GenreTitle


admin.site.register(User)
admin.site.register(Review)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(Title)
admin.site.register(Genre)
admin.site.register(GenreTitle)


class BaseAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
