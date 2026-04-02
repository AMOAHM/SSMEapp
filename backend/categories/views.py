from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema

from .models import Category
from .serializers import CategorySerializer


class CategoryListCreateView(generics.ListCreateAPIView):
    """List and create categories."""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = None
    # filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # search_fields = ['name', 'description']
    # ordering_fields = ['name', 'created_at']
    # ordering = ['name']
    
    @extend_schema(
        summary="List categories",
        description="Retrieve a list of all active business categories.",
        responses={200: CategorySerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create category",
        description="Create a new business category (admin only).",
        responses={201: CategorySerializer}
    )
    def post(self, request, *args, **kwargs):
        # Only admin users can create categories
        if not request.user.is_admin_user():
            return Response(
                {'error': 'Only administrators can create categories.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().post(request, *args, **kwargs)


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete categories."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get category details",
        description="Retrieve detailed information about a specific category.",
        responses={200: CategorySerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update category",
        description="Update category information (admin only).",
        responses={200: CategorySerializer}
    )
    def patch(self, request, *args, **kwargs):
        if not request.user.is_admin_user():
            return Response(
                {'error': 'Only administrators can update categories.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete category",
        description="Delete a category (admin only).",
        responses={204: None}
    )
    def delete(self, request, *args, **kwargs):
        if not request.user.is_admin_user():
            return Response(
                {'error': 'Only administrators can delete categories.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().delete(request, *args, **kwargs)


@extend_schema(
    summary="Get popular categories",
    description="Retrieve categories with the most businesses.",
    responses={200: CategorySerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def popular_categories(request):
    """Get popular categories based on business count."""
    categories = Category.objects.filter(is_active=True).order_by('-businesses__count')[:10]
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)
