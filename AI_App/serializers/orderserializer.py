from rest_framework import serializers
from ..models import Order,OrderItem
from .productserializer import ProductSerializer, VariantSerializer, SizeSerializer


class OrderlItemListViewSerializr(serializers.ModelSerializer):
    ProductName = serializers.CharField(source='variant.product.name', read_only=True)
    image = serializers.ImageField(source='variant.product.image', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['ProductName', 'quantity','price','image']



class OrderlListViewSerializr(serializers.ModelSerializer):
    items = OrderlItemListViewSerializr(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id','items','total_amount','status','created_at']