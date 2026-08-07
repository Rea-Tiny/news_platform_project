from django.shortcuts import render
from rest_framework import permissions, status, viewsets 
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import Article 
from .serializers import ArticleSerializer 
    

# Create your views here.
def home_view(request):
    """Render the default homepage displaying approved articles."""
    articles = Article.objects.filter(approved=True)
    return render(request, "news_api/index.html", {"articles": articles})

class IsJournalist(permissions.BasePermission):
    """Custom permission class to restrict actions to journalist users."""
    def has_permission(self, request, view):
        """Check if the requesting user is authenticated and has the 'journalist' role."""
        return (
            request.user.is_authenticated and getattr(request.user, "role", "") == "journalist"
        )

class IsEditor(permissions.BasePermission):
    """Custom permission class to restrict actions to editor users."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and request.user.role == "editor"
        )

class ArticleViewSet(viewsets.ModelViewSet):
    """API endpoint viewset for managing articles."""

    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def get_permissions(self):
        """Instantiate and return the list of permissions required for this action."""
        if self.action == "create":
            return [IsJournalist()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """Save the new article instance and set the current user as author."""
        serializer.save(author=self.request.user)
    
    @action(
        detail=True, 
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
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
        """Retrieve approved articles from publishers  the current user subscribes to."""
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