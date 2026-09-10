from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'articles', views.ArticleViewSet, basename='article')

urlpatterns = [
    path('', views.home_view, name="home"),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('article/create/', views.create_article_web, name='create_article'),
    path(
        'article/approve/<int:pk>/',
        views.approve_article_web,
        name='approve_article_web',
    ),
    path('publisher/create/', views.create_publisher_web, name='create_publisher'),
    path('newsletter/create/', views.create_newsletter_web, name='create_newsletter'),
    path('api/', include(router.urls)),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('approved/', views.log_approved_article, name='log_approved'),
]