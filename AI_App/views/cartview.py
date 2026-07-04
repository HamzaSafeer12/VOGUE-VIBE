from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from ..models import CartItem
from ..serializers import CartItemSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication

class CartView(APIView):
    # Sirf un users ko access do jo logged in hain
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    # 1. GET: User ka poora cart dikhao
    def get(self, request):
        # Filter taaki sirf isi user ke items milain
        items = CartItem.objects.filter(user=request.user).select_related(
            'variant__product', 'variant__size'
        )
        serializer = CartItemSerializer(items, many=True)
        return Response(serializer.data)

    # 2. POST: Cart mein item add karo ya quantity barhao
    def post(self, request):
        # Humne context={'request': request} isliye bheja taaki Serializer ko pata chale user kaun hai
        serializer = CartItemSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save() # Yeh tumhare Serializer wala 'create' method chalaye ga
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # 3. DELETE: Cart se poora item khatam kar do
    # Is ke liye hum query parameter use karenge: /api/cart/?item_id=5
    def delete(self, request):
        item_id = request.query_params.get('item_id')
        try:
            item = CartItem.objects.get(id=item_id, user=request.user)
            item.delete()
            return Response({"message": "Item removed from cart"}, status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)