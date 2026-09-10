from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .forms import CustomUserCreationForm
from .models import Article, Publisher, Newsletter
from .serializers import ArticleSerializer, PublisherSerializer, NewsletterSerializer, UserSerializer


# Create your views here.
def home_view(request):
    """Render the default homepage displaying approved articles."""
    articles = Article.objects.filter(approved=True)
    return render(request, "news_api/home.html", {"articles": articles})


def register_view(request):
    """Handle user account creation and registration."""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = CustomUserCreationForm()
    return render(request, "news_api/register.html", {"form": form})


def login_view(request):
    """Handle user authentication and login."""
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")
    else:
        form = AuthenticationForm()
    return render(request, "news_api/login.html", {"form": form})


def logout_view(request):
    """Handles user logout."""
    logout(request)
    return redirect("home")


@login_required
def dashboard_view(request):
    """Render role-specific poratl for authenticated user."""
    user = request.user
    context = {}

    if getattr(user, "role", "") == "editor":
        context["pending_articles"] = Article.objects.filter(approved=False)
        context["newsletter"] = Newsletter.objects.all()
    elif getattr(user, "role", "") == "journalist":
        context["publishers"] = Publisher.objects.all()
        context["newsletter"] = Newsletter.objects.filter(author=user)
    elif getattr(user, "role", "") == "reader":
        publishers = user.subscribed_publishers.all()
        context["articles"] = Article.objects.filter(
            publisher__in=publishers, approved=True
        )
        context["newsletter"] = Newsletter.objects.all()

    return render(request, "news_api/dashboard.html", context)


@login_required
def create_publisher_web(request):
    """Allow editors to create a new Publisher."""
    if request.method == "POST" and getattr(
        request.user, "role", ""
    ) == "editor":
        name = request.POST.get("name")
        Publisher.objects.create(name=name)
    return redirect("dashboard")


@login_required
def create_newsletter_web(request):
    """Allow journalists and editors to create newsletter."""
    if request.method == "POST" and getattr(
        request.user, "role", ""
    ) in ["journalist", "editor"]:
        title = request.POST.get("title")
        content = request.POST.get("content")
        Newsletter.objects.create(
            title=title, content=content, author=request.user
        )
    return redirect("dashboard")


@login_required
def create_article_web(request):
    """Hanlde article creation submission."""
    if request.method == "POST" and getattr(
        request.user, "role", ""
    ) == "journalist":
        title = request.POST.get("title")
        content = request.POST.get("content")
        publisher_id = request.POST.get("publisher_id")
        Article.objects.create(
            title=title,
            content=content,
            publisher_id=publisher_id,
            author=request.user,
            approved=False,
        )
    return redirect("dashboard")


@login_required
def approve_article_web(request, pk):
    """Handle article approval action from Editor Dashboard."""
    if request.method == "POST" and getattr(
        request.user, "role", ""
    ) == "editor":
        try:
            article = Article.objects.get(pk=pk)
            article.approved = True
            article.save()
        except Article.DoesNotExist:
            pass
    return redirect("dashboard")


class IsJournalist(permissions.BasePermission):
    """Custom permission class to restrict actions to journalist users."""
    def has_permission(self, request, view):
        """Check if the requesting user is authenticated and has the
        Journalist role."""
        return (
            request.user.is_authenticated
            and getattr(request.user, "role", "") == "journalist"
        )


class IsEditor(permissions.BasePermission):
    """Custom permission class to restrict actions to editor users."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            getattr(request.user, "role", "") == "editor"
        )


class ArticleViewSet(viewsets.ModelViewSet):
    """API endpoint viewset for managing articles."""

    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def get_permissions(self):
        """Instantiate and return the list of permissions
        required for this action."""
        if self.action == "create":
            return [IsJournalist()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """Save the new article instance and set the current user as author."""
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsEditor],
    )
    def approve(self, request, pk=None):
        """Approve a specific pending article."""
        article = self.get_object()
        article.approved = True
        article.save()
        return Response(
            {"status": "Article approved successfully."},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscribed(self, request):
        """Retrieve approved articles from publishers  the current
          user subscribes to."""
        publishers = request.user.subscribed_publishers.all()
        articles = Article.objects.filter(
            publisher__in=publishers, approved=True
        )
        serializer = self.get_serializer(articles, many=True)
        return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def log_approved_article(request):
    """API endpoint view to list all approved articles in JSON format."""
    approved_articles = Article.objects.filter(approved=True)
    serializer = ArticleSerializer(approved_articles, many=True)
    return Response(serializer.data)
