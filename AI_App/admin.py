from django.utils.html import format_html
from django.contrib import admin
from .models import Category, Product, Profile, ProductVariant,Size, CartItem, Order, OrderItem # Humne __init__ mein define kiya tha isliye direct import ho jayenge

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)} # Name likhte hi slug khud ban jayega


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1  # Khali rows kitni dikhni chahiye
    min_num = 1 # Kam az kam ek size hona lazmi hai (optional)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'get_total_stock', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')
    
    # 2. Variants ko product ke page par hi add kar dein
    inlines = [ProductVariantInline]

    # Ek professional touch: Sare sizes ka total stock list mein dikhana
    def get_total_stock(self, obj):
        from django.db.models import Sum
        total = obj.variants.aggregate(Sum('stock'))['stock__sum']
        return total if total else 0
    get_total_stock.short_description = 'Total Stock'

    # 2. Edit page ke andar dikhane ke liye
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" />', obj.image.url)
        return "No Image"

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    # Admin list mein ye columns nazar ayenge
    list_display = ['id', 'user', 'get_product_name', 'get_size', 'quantity', 'added_at']
    
    # Filter lagane ke liye (side bar mein)
    list_filter = ['user', 'added_at']
    
    # Search karne ke liye
    search_fields = ['user__username', 'variant__product__name']

    # Custom methods taaki variant ke andar ka data list mein dikh sake
    def get_product_name(self, obj):
        return obj.variant.product.name
    get_product_name.short_description = 'Product'

    def get_size(self, obj):
        return obj.variant.size.name
    get_size.short_description = 'Size'



# Professional way: Order ke andar hi items dikhana
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0 # Extra khali rows nahi dikhayega
    readonly_fields = ('variant', 'price', 'quantity') # Taki admin galti se price na badal de
    can_delete = False # History record hai, isliye delete ka option hatana behtar hai

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Bahar se list mein kya kya nazar aaye
    list_display = ('id', 'user', 'full_name', 'total_amount', 'status', 'is_paid', 'created_at')
    
    # Kin cheezon se filter kar sakein
    list_filter = ('status', 'is_paid', 'created_at')
    
    # Search bar kin fields par kaam kare
    search_fields = ('id', 'full_name', 'email', 'stripe_checkout_id')
    
    # Order items ko inline dikhao
    inlines = [OrderItemInline]
    
    # Professional touch: Status ko chor kar baaki sab readonly kar dena behtar hai
    # taaki purana order data change na ho sake
    readonly_fields = ('user', 'total_amount', 'stripe_checkout_id', 'created_at')

    # Fields ki grouping (optional but professional)
    fieldsets = (
        ('Customer Info', {
            'fields': ('user', 'full_name', 'email', 'phone')
        }),
        ('Shipping Address', {
            'fields': ('address', 'city', 'zip_code')
        }),
        ('Payment & Status', {
            'fields': ('total_amount', 'stripe_checkout_id', 'is_paid', 'status')
        }),
    )