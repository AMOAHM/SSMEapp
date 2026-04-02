from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Review
from .serializers import ReviewSerializer, ReviewCreateSerializer


class ReviewListCreateView(generics.ListCreateAPIView):
    """List and create reviews."""
    queryset = Review.objects.select_related('user', 'business')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # filter_backends = [DjangoFilterBackend]
    # filterset_class = ReviewFilter
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReviewCreateSerializer
        return ReviewSerializer
    
    @extend_schema(
        summary="List reviews",
        description="Retrieve a list of reviews with filtering capabilities.",
        parameters=[
            OpenApiParameter('business', OpenApiTypes.INT, description='Business ID'),
            OpenApiParameter('rating', OpenApiTypes.INT, description='Exact rating'),
            OpenApiParameter('min_rating', OpenApiTypes.INT, description='Minimum rating'),
            OpenApiParameter('max_rating', OpenApiTypes.INT, description='Maximum rating'),
        ],
        responses={200: ReviewSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create review",
        description="Create a new review for a business (authenticated users only).",
        responses={201: ReviewSerializer}
    )
    def post(self, request, *args, **kwargs):
        # Only customers can create reviews
        if request.user.role != 'customer':
            return Response(
                {'error': 'Only customers can create reviews.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().post(request, *args, **kwargs)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete reviews."""
    queryset = Review.objects.select_related('user', 'business')
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        obj = super().get_object()
        # Users can only view/edit their own reviews
        if obj.user != self.request.user and not self.request.user.is_admin_user():
            raise permissions.PermissionDenied("You can only access your own reviews.")
        return obj
    
    @extend_schema(
        summary="Get review details",
        description="Retrieve detailed information about a specific review.",
        responses={200: ReviewSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update review",
        description="Update a review (review owner only).",
        responses={200: ReviewSerializer}
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete review",
        description="Delete a review (review owner or admin only).",
        responses={204: None}
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


@extend_schema(
    summary="Get business reviews",
    description="Retrieve all reviews for a specific business.",
    responses={200: ReviewSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def business_reviews(request, business_id):
    """Get all reviews for a specific business."""
    reviews = Review.objects.filter(business_id=business_id).select_related('user')
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)


@extend_schema(
    summary="Get user reviews",
    description="Retrieve all reviews written by the current user.",
    responses={200: ReviewSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_reviews(request):
    """Get all reviews written by the current user."""
    reviews = Review.objects.filter(user=request.user).select_related('business')
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)
