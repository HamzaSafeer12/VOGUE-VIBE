from rest_framework import serializers
from ..models import CartItem, ProductVariant
from ..serializers import CartItemVariantSerializer
# Purane serializers ko bhi import kar lena jo humne pehle banaye thay

class CartItemSerializer(serializers.ModelSerializer):
    # Dikhane ke liye humein variant ki poori detail chahiye
    variant_details = CartItemVariantSerializer(source='variant', read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'variant', 'variant_details', 'quantity', 'total_price']
        # 'variant' field user se ID legi (Write)
        # 'variant_details' frontend ko poora data dikhayegi (Read)

    def get_total_price(self, obj):
        return obj.get_total_price()

    def create(self, validated_data):
        # Yahan hum wo logic likhenge jo quantity update karega
        user = self.context['request'].user
        variant = validated_data['variant']
        quantity = validated_data.get('quantity', 1)

        # Check: Kya ye item pehle se cart mein hai?
        cart_item, created = CartItem.objects.get_or_create(
            user=user, 
            variant=variant,
            defaults={'quantity': quantity}
        )

        if not created:
            # Agar pehle se tha, toh sirf quantity barha do
            cart_item.quantity += quantity
            cart_item.save()
        
        return cart_item