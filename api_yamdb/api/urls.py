from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, CommentViewSet, CreateUserViewSet,
                    GenreViewSet, GetTokenViewSet, ReviewViewSet, TitleViewSet,
                    UsersViewSet)

router = DefaultRouter()
router.register('auth/signup', CreateUserViewSet)
router.register('users', UsersViewSet, basename='users')
router.register("categories", CategoryViewSet)
router.register("genres", GenreViewSet)
router.register("titles", TitleViewSet)
router.register(
    r"titles/(?P<title_id>\d+)/reviews", ReviewViewSet, basename='reviews'
)
router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename='coomments'
)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/token/', GetTokenViewSet.as_view()),
]
