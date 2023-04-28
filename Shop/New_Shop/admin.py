from django.contrib import admin
from .models import *


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'mobile', 'address', 'get_user_email', 'get_user_first_and_last_name', 'img_preview')
    search_fields = ('name',)
    readonly_fields = ('img_preview',)

    def get_user_email(self, obj):
        return obj.user.email

    def get_user_first_and_last_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'

    get_user_email.short_description = 'Email'
    get_user_first_and_last_name.short_description = 'Full Name'


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'img_preview')
    search_fields = ('name',)
    readonly_fields = ('img_preview',)
    prepopulated_fields = {'slug': ('name',)}


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'price', 'category', 'stock', 'available', 'created', 'updated', 'img_preview')
    list_filter = ('available', 'created', 'updated')
    list_editable = ('price', 'stock', 'available')
    search_fields = ('name',)
    readonly_fields = ('img_preview', 'slug')



class ProductInline(admin.TabularInline):
    model = Order.product.through
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer_username', 'email', 'status', 'created', 'updated')
    search_fields = ('customer_username',)
    list_editable = ('status',)
    inlines = [ProductInline]


class SubscribedUsersAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'created_date')
    search_fields = ('email', 'name')


class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('promo_code', 'discount', 'start_date', 'end_date', 'max_use', 'used_count')


admin.site.register(PromoCode, PromoCodeAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(SubscribedUser, SubscribedUsersAdmin)
