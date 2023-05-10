from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from reviews.models import Titles, Categories, Genres, Review, Comment


class TitleSerializer(serializers.ModelSerializers):
    class Meta:
        fields = '__all__'
        model = Titles


class CategoriesSerializer(serializers.ModelSerializers):
    class Meta:
        fields = '__all__'
        model = Categories


class GenresSerializer(serializers.ModelSerializers):
    class Meta:
        fields = '__all__'
        model = Genres


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Review (Ревью произведений).
    """
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = '__all__'
        model = Review

    def validate(self, attrs):
        """
        Проверяет, что пользователь
        не оставляет отзыв на одно произведение дважды.
        Args:
            attrs (dict): Входные данные, которые требуется проверить.
        Raises:
            serializers.ValidationError: Выбрасывается, если пользователь уже
            оставил отзыв с указанным title_id.
        Returns:
            dict: Проверенные и валидные данные.
        """
        request = self.context['request']
        if request.method == 'POST':
            title_id = request.parser_context['kwargs'].get('title_id')
        user = request.user
        if user.reviews.filter(title_id=title_id).exists():
            raise serializers.ValidationError(
                'Нельзя оставить отзыв на одно произведение дважды'
            )
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Comment (Комментарии).
    """
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
