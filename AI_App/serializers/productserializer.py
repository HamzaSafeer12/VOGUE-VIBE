from rest_framework import serializers
from ..models import Product,Size,ProductVariant
# class ProductSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Product
#         fields = '__all__' # Saari fields dikhane ke liye
#         depth = 1  # Is se Category ki details bhi mil jayengi (sirf ID nahi)


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['name'] # Sirf size ka naam chahiye (e.g., Small)

class VariantSerializer(serializers.ModelSerializer):
    # 'size' ki poori detail nikalne ke liye upar wala serializer use karein
    size = SizeSerializer(read_only=True) 
    
    class Meta:
        model = ProductVariant
        fields = ['id', 'size', 'stock']


class CartItemVariantSerializer(serializers.ModelSerializer):
    size = SizeSerializer(read_only=True)
    # size = serializers.CharField(source='size.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    image = serializers.ImageField(source='product.image', read_only=True)

    class Meta:
        model = ProductVariant
        fields = ['id', 'size', 'stock', 'product_name', 'price', 'image']

class ProductSerializer(serializers.ModelSerializer):
    # 'variants' wahi related_name hai jo humne model mein rakha tha
    variants = VariantSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'category_name', 'name', 
            'description', 'price', 'image', 'variants', 'created_at'
        ]