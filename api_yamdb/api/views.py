from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.decorators import action
from rest_framework.serializers import ValidationError
from rest_framework.filters import SearchFilter


from api.serializers import (
    TitleSerializer,
    GenresSerializer,
    CategoriesSerializer,
    ReviewSerializer,
    CommentSerializer,
    UserSerializer,
    UserRoleSerializer,
    TokenSerializer,
    SignupSerializer,
)

from reviews.models import Title, Categorie, Genre, User, Review, Comment
from api.permissions import IsAdmin, IsAdminAuthorModeratorOrReadOnly


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'username'
    search_fields = ('username',)
    filter_backends = (SearchFilter,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        methods=['get', 'patch'],
        detail=False,
        url_path='me',
        permission_classes=(IsAuthenticated,),
    )
    def get_patch(self, request):
        user = get_object_or_404(User, username=self.request.user)
        if request.method == 'GET':
            serializer = UserRoleSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = UserRoleSerializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class TitleVewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer


class CategoriesViewSet(viewsets.ModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategoriesSerializer


class GenresViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenresSerializer


class ReviewVeiewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminAuthorModeratorOrReadOnly]

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAdminAuthorModeratorOrReadOnly]

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')

        title = get_object_or_404(Title, id=title_id)
        review = title.reviews.filter(id=review_id).first()

        if review is None:
            raise ValueError('У произведения нет такого отзыва')

        queryset = review.comments.all()
        return queryset

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')

        title = get_object_or_404(Title, id=title_id)
        review = title.reviews.filter(id=review_id).first()

        if review is None:
            raise ValueError('У произведения нет такого отзыва')

        serializer.save(author=self.request.user, review=review)


class SignupView(CreateAPIView):
    permission_classes = [AllowAny]

    def create(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = User.objects.get(email=serializer.data['email'])
        confirmation_code = default_token_generator.make_token(user)
        email_data = {
            'subject': 'Добро пожаловать на наш сайт!',
            'message': f'Your confirmation_code: {confirmation_code}',
            'from_email': settings.TOKEN_EMAIL,
            'recipient_list': [user.email],
        }
        send_mail(**email_data)

        return Response({'email': user.email, 'username': user.username})


class TokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User,
            username=serializer.validated_data['username'],
        )
        if not default_token_generator.check_token(
            user, serializer.validated_data['confirmation_code']
        ):
            raise ValidationError('Неверный код подтверждения.')
        token = AccessToken().for_user(user)
        return Response({'token': str(token)})
