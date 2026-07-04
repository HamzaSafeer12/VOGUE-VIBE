from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Product
from ..serializers import ProductSerializer
from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny

class ProductListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        category_id = request.query_params.get('category')
        
        # --- TABDEELI YAHAN HAI ---
        # 1. select_related: Category ke liye (Forward Link)
        # 2. prefetch_related: Variants aur unke Sizes ke liye (Reverse & Nested Link)
        products = Product.objects.select_related('category').prefetch_related(
            'variants__size'
        ).all().order_by('-id')
        # --------------------------

        if category_id:
            products = products.filter(category_id=category_id)
        
        paginator = PageNumberPagination()
        paginated_products = paginator.paginate_queryset(products, request)
        
        serializer = ProductSerializer(paginated_products, many=True)
        return paginator.get_paginated_response(serializer.data)


class ProductDetailView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, pk):
        product = get_object_or_404(Product.objects.select_related('category').prefetch_related('variants__size'), pk=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
def home_page(request):
    return render(request, 'home.html')