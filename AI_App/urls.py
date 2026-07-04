from django.urls import path
from .views.genericviews import FirstCallAI, LangChainClass, Promptchainsmodel, chainpromptmodel_OutPut_Parser,GoogleGenAIModel,RestaurantAgentView
from .views.simplechatbot1 import simplechatbotclass
from .views.signupview import SignupAPIView
from .views.productview import ProductListView,ProductDetailView,home_page
from .views.categoryview import CategoryListView
from .views.loginview import login_page
from .views.cartview import CartView
from .views.ordercheckoutview import CreateCheckoutSessionView, VerifyPaymentView, OrderListView
from django.views.generic import TemplateView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("api/ai-response/", FirstCallAI.as_view(), name="ai-response"),
    path("api/langchainResponse/", LangChainClass.as_view(), name="LangchainResponse"),
    path("api/promotchainmodelResponse/",Promptchainsmodel.as_view(),name="PromptchainsmodelResponse"),
    path("api/promotchainmodel_Output_ParserResponse/",chainpromptmodel_OutPut_Parser.as_view(),name="chainpromptmodel_OutPut_ParserResponse"),
    path("api/GoogleGenAIModel/",GoogleGenAIModel.as_view(),name="GoogleGenAIModel"),
    path("api/RestaurantAgentView/",RestaurantAgentView.as_view(),name="RestaurantAgentView"),
    path("api/simplechatbot/",simplechatbotclass.as_view(),name="simplechatbot"),
    path('api/signup/', SignupAPIView.as_view(), name='api-signup'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/products/', ProductListView.as_view(), name='product-list'),
    path('api/product/detail/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('', home_page, name='home'),
    path('login/', login_page, name='login'),
    path('api/categories/', CategoryListView.as_view(), name='category-list'),
    path('api/cart/', CartView.as_view(), name='cart-api'),
    path('cart-page/', TemplateView.as_view(template_name='cart.html'), name='cart-page'),
    path('api/checkout/', CreateCheckoutSessionView.as_view(), name='checkout'),  
    path('payment-success/', TemplateView.as_view(template_name='payment_success.html'), name='payment-success-page'),
    path('api/verify-payment/', VerifyPaymentView.as_view(), name='verify-payment-api'),
    path('api/ordersrecord/', OrderListView.as_view(), name='checkout'),
    path('myorders/', TemplateView.as_view(template_name='orderrecord.html'), name='orders-page'),
]
