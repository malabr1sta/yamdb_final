from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre, Review, Title, User

from .filter import TitleFilter
from .permissions import Admin, IsAdminModeratorOrReadOnly, IsAdminOrReadOnly
from .serializers import (CategorySerializer, CommentSerializer,
                          CreateUserSerializer, GenreSerializer,
                          ReviewSerializer, TitleGetSerializer,
                          TitlePostUpdateSerializer, TokenSerializer,
                          UserMeSerializer, UserSerializer)


class GetTokenViewSet(APIView):
    """Класс для работы выдачи токена"""

    serializer_class = TokenSerializer
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(User, username=serializer.data['username'])
        confirmation_code = serializer.data['confirmation_code']
        if default_token_generator.check_token(user, confirmation_code):
            token = AccessToken.for_user(user)
            return Response(
                {'token': str(token)}, status=status.HTTP_200_OK
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)


class CreateUserViewSet(CreateModelMixin, GenericViewSet):
    """Класс для заведения пользователей"""

    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        new_user = serializer.save()
        confirmation_token = default_token_generator.make_token(new_user)
        send_mail(
            'Your verification token',
            confirmation_token,
            settings.FROM_EMAIL,
            [new_user.email],
            fail_silently=False,
        )

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UsersViewSet(viewsets.ModelViewSet):
    """Класс для обработки запросов к модели User"""

    permission_classes = (Admin,)
    lookup_field = "username"
    pagination_class = LimitOffsetPagination
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('username',)

    @action(
        detail=False, url_path='me',
        permission_classes=[IsAuthenticated], methods=["get", "patch"]
    )
    def me(self, request):
        if request.method == 'GET':
            queryset = User.objects.get(username=request.user)
            serializer = UserMeSerializer(queryset)
            return Response(serializer.data)
        if request.method == 'PATCH':
            data1 = request.data
            if ('role' in data1):
                data1._mutable = True
                data1['role'] = request.user.role
            serializer = UserMeSerializer(
                request.user, data=data1, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class ListCreateDestroy(mixins.ListModelMixin, mixins.CreateModelMixin,
                        mixins.DestroyModelMixin, viewsets.GenericViewSet):

    pass


class CategoryViewSet(ListCreateDestroy):
    """Класс представления модели Category."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)


class GenreViewSet(ListCreateDestroy):
    """Класс представления модели Genre."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)


class TitleViewSet(viewsets.ModelViewSet):
    """Класс представления модели Title."""

    queryset = Title.objects.all()
    filter_backends = (DjangoFilterBackend,)
    http_method_names = ["get", "post", "delete", "patch"]
    permission_classes = (IsAdminOrReadOnly,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return TitleGetSerializer
        return TitlePostUpdateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorOrReadOnly,)

    def get_queryset(self):
        title = Title.objects.get(pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        author = self.request.user
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        if Review.objects.filter(title=title, author=author).exists():
            raise serializers.ValidationError(
                'Вы  может оставить только один отзыв на произведение.'
            )
        serializer.save(author=author, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminModeratorOrReadOnly,)
    serializer_class = CommentSerializer

    def get_queryset(self):
        review = Review.objects.get(pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
