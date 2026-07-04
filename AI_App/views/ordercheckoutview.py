import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db import transaction
from ..models import Order, OrderItem, CartItem
from ..serializers import OrderlItemListViewSerializr, OrderlListViewSerializr

class CreateCheckoutSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        user = request.user
        
        # 1. User ka cart uthain
        cart_items = CartItem.objects.filter(user=user)

        if not cart_items.exists():
            return Response({"error": "Aapka cart khali hai!"}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Stripe ke liye items ki list (Line Items) taiyar karein
        line_items = []
        total_amount = 0
        for item in cart_items:
            product_price = item.variant.product.price
            total_amount += product_price * item.quantity
            
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': item.variant.product.name,
                        'images': [request.build_absolute_uri(item.variant.product.image.url)] if item.variant.product.image else [],
                    },
                    'unit_amount': int(product_price * 100), # Cents mein conversion
                },
                'quantity': item.quantity,
            })

        try:
            # 3. "Atomic Transaction" - Sab kuch ek saath save hoga ya kuch bhi nahi
            with transaction.atomic():
                
                # A. Pehle Database mein Order record create karein (Metadata ke liye ID zaroori hai)
                order = Order.objects.create(
                    user=user,
                    full_name=request.data.get('full_name'),
                    email=user.email,
                    phone=request.data.get('phone'),
                    address=request.data.get('address'),
                    city=request.data.get('city'),
                    zip_code=request.data.get('zip_code'),
                    total_amount=total_amount,
                    status='Pending' # Default status
                )

                # B. Cart items ko OrderItems mein copy karein
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        variant=item.variant,
                        price=item.variant.product.price,
                        quantity=item.quantity
                    )

                # C. Stripe Session banayein (Ab hamare paas order.id mojud hai)
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=line_items,
                    mode='payment',
                    # Success URL mein session_id query param bhej rahe hain frontend ke liye
                    success_url='http://127.0.0.1:8000/payment-success/?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url='http://127.0.0.1:8000/payment-failed/',
                    customer_email=user.email,
                    # YEH SAB SE ZAROORI HAI: Metadata Stripe ko bhej rahe hain
                    metadata={
                        'order_id': order.id
                    }
                )

                # D. Order ko Stripe ki Session ID se update karein (Future reference ke liye)
                order.stripe_checkout_id = checkout_session.id
                order.save()

                # Cart khali nahi kiya (Success view ya Webhook karega)
                return Response({'url': checkout_session.url}, status=status.HTTP_200_OK)

        except Exception as e:
            # transaction.atomic ki wajah se agar yahan error aaya to Order aur OrderItems delete ho jayenge
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class VerifyPaymentView(APIView):
    # Sirf logged-in user hi apna order verify kar sakta hai
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # 1. Frontend se session_id pakarna
        session_id = request.GET.get('session_id')
        
        if not session_id:
            return Response({"error": "Session ID missing!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 2. Stripe API key set karna
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            # 3. Stripe se is session ki mukammal detail mangwana
            # Retrieve session with metadata
            session = stripe.checkout.Session.retrieve(session_id)

            # 4. Check karna ke kya payment waqayi ho chuki hai
            if session.payment_status == 'paid':
                
                # Metadata se hamari database wali Order ID nikalna
                order_id = session.metadata.get('order_id')
                
                try:
                    # Database mein Order dhoondna
                    order = Order.objects.get(id=order_id, user=request.user)
                    
                    # 5. Agar order pehle hi 'Paid' nahi hai toh update karein
                    # (Yeh isliye ke agar page refresh ho toh dobara mehnat na ho)
                    if order.status != 'Paid':
                        order.status = 'Paid'
                        # Optional: Stripe ki transaction ID bhi save kar len record ke liye
                        order.stripe_checkout_id = session.id 
                        order.save()
                        
                        # 6. ASLI BACKEND KAAM: Cart khali karna
                        # Payment confirm ho gayi, ab purani items cart se hata do
                        CartItem.objects.filter(user=request.user).delete()
                        
                        return Response({
                            "message": "Payment verified and order updated!",
                            "order_id": order.id
                        }, status=status.HTTP_200_OK)
                    else:
                        return Response({"message": "Order already processed."}, status=status.HTTP_200_OK)

                except Order.DoesNotExist:
                    return Response({"error": "Order record not found in our database."}, status=status.HTTP_404_NOT_FOUND)
            
            else:
                return Response({"error": "Payment has not been completed yet."}, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.StripeError as e:
            # Stripe ki taraf se koi technical error
            return Response({"error": f"Stripe error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            # Koi bhi aur unexpected error
            return Response({"error": f"Something went wrong: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class OrderListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).prefetch_related('items__variant__product').all().order_by('-id')

# products = Product.objects.select_related('category').prefetch_related(
#             'variants__size'
#         ).all().order_by('-id')

        serializer = OrderlListViewSerializr(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

