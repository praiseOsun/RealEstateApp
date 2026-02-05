from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Listing
from .serializers import ListingSerializer
from django.db.models import Q
from .permissions import IsRealtor

class ManageListingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Get listings for the logged-in realtor.
        Optional query parameter: ?slug=<slug>
        """
        user = request.user
        if user.role != 'realtor':
            return Response({'error': 'Only realtors can view listings.'}, status=status.HTTP_403_FORBIDDEN)

        slug = request.query_params.get('slug')
        if slug:
            listing = Listing.objects.filter(realtor=user, slug=slug).first()
            if not listing:
                return Response({'error': 'Listing not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = ListingSerializer(listing)
            return Response({'listing': serializer.data}, status=status.HTTP_200_OK)
        else:
            listings = Listing.objects.filter(realtor=user).order_by('-created_at')
            serializer = ListingSerializer(listings, many=True)
            return Response({'listings': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a new listing.
        """
        user = request.user
        if user.role != 'realtor':
            return Response({'error': 'Only realtors can create listings.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ListingSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(
            realtor=user,
            realtor_email=user.email
        )
        return Response({'message': 'Listing created successfully.', 'listing': serializer.data},
                        status=status.HTTP_201_CREATED)

    def put(self, request):
        """
        Full update of a listing (requires slug in request data).
        """
        user = request.user
        if user.role != 'realtor':
            return Response({'error': 'Only realtors can update listings.'}, status=status.HTTP_403_FORBIDDEN)

        slug = request.data.get('slug')
        if not slug:
            return Response({'error': 'Slug is required to update a listing.'}, status=status.HTTP_400_BAD_REQUEST)

        listing = Listing.objects.filter(realtor=user, slug=slug).first()
        if not listing:
            return Response({'error': 'Listing not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ListingSerializer(listing, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': 'Listing updated successfully.', 'listing': serializer.data},
                        status=status.HTTP_200_OK)

    def patch(self, request):
        """
        Partial update of a listing (e.g., publish/unpublish).
        Requires slug in request data.
        """
        user = request.user
        if user.role != 'realtor':
            return Response({'error': 'Only realtors can update listings.'}, status=status.HTTP_403_FORBIDDEN)

        slug = request.data.get('slug')
        if not slug:
            return Response({'error': 'Slug is required to update a listing.'}, status=status.HTTP_400_BAD_REQUEST)

        listing = Listing.objects.filter(realtor=user, slug=slug).first()
        if not listing:
            return Response({'error': 'Listing not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ListingSerializer(listing, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': 'Listing updated successfully.', 'listing': serializer.data},
                        status=status.HTTP_200_OK)

    def delete(self, request):
        """
        Delete a listing by slug.
        """
        user = request.user
        if user.role != 'realtor':
            return Response({'error': 'Only realtors can delete listings.'}, status=status.HTTP_403_FORBIDDEN)

        slug = request.data.get('slug')
        if not slug:
            return Response({'error': 'Slug is required to delete a listing.'}, status=status.HTTP_400_BAD_REQUEST)

        listing = Listing.objects.filter(realtor=user, slug=slug).first()
        if not listing:
            return Response({'error': 'Listing not found.'}, status=status.HTTP_404_NOT_FOUND)

        listing.delete()
        return Response({'success': 'Listing deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


class ListingDetailView(APIView):
    def get(self, request,format=None):
        try:
            slug = request.query_params.get('slug')

            if not slug:
                return Response(
                    {'error': 'Slug parameter is required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not Listing.objects.filter(slug=slug, is_published=True).exists():
                return Response(
                    {'error':'Published listing with this slug does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            listing = Listing.objects.get(slug=slug, is_published=True)
            serializer = ListingSerializer(listing)

            return Response(
                {'listing': serializer.data},
                status=status.HTTP_200_OK
            )

        except:
            return Response(
                {'error': 'An error occurred while retrieving the listing detail.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class ListingsView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        try:
            if not Listing.objects.filter(is_published=True).exists():
                return Response(
                    {'error': 'No published listings found in the database.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            listings = Listing.objects.filter(is_published=True).order_by('-created_at')
            serializer = ListingSerializer(listings, many=True)
            return Response(
                {'listings': serializer.data},
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response(
                {'error': 'An error occurred while retrieving listings.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class SearchListingsView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        # Base queryset
        listings = Listing.objects.filter(is_published=True)

        # -----------------------
        # 🔍 SEARCH (REQUIRED)
        # -----------------------
        search = request.query_params.get('search')

        if search:
            listings = listings.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location__icontains=search) |
                Q(category__icontains=search)
            )
        # -----------------------
        # 🎯 FILTERS (OPTIONAL)
        # -----------------------

        max_price = request.query_params.get('max_price')
        if max_price:
            try:
                listings = listings.filter(price__lte=float(max_price))
            except ValueError:
                return Response(
                    {'error': 'Invalid max_price parameter.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        bedrooms = request.query_params.get('bedrooms')
        if bedrooms:
            try:
                listings = listings.filter(bedrooms__gte=int(bedrooms))
            except ValueError:
                return Response(
                    {'error': 'Invalid bedrooms parameter.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        bathrooms = request.query_params.get('bathrooms')
        if bathrooms:
            try:
                listings = listings.filter(bathrooms__gte=round(float(bathrooms), 1))
            except ValueError:
                return Response(
                    {'error': 'Invalid bathrooms parameter.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        location = request.query_params.get('location')
        if location:
            listings = listings.filter(location__icontains=location)

        category = request.query_params.get('category')
        valid_categories = [choice[0].upper() for choice in Listing.CategoryChoices.choices]
        if category and category.upper() in valid_categories:
            listings = listings.filter(category=category.upper())

        # -----------------------
        # 📦 ORDER + RESPONSE
        # -----------------------

        listings = listings.order_by('-created_at')

        if not listings.exists():
            return Response(
                {'error': 'No listings found matching the criteria.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ListingSerializer(listings, many=True)

        return Response(
            {
                'count': listings.count(),
                'results': serializer.data
            },
            status=status.HTTP_200_OK
        )
