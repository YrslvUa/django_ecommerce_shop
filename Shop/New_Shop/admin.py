from django.contrib import admin
from .models import *


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'mobile', 'address', 'img_preview')
    search_fields = ('name',)
    readonly_fields = ('img_preview',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'img_preview')
    search_fields = ('name',)
    readonly_fields = ('img_preview',)
    prepopulated_fields = {'slug': ('name',)}


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'stock', 'available', 'created', 'updated', 'img_preview')
    list_filter = ('available', 'created', 'updated')
    list_editable = ('price', 'stock', 'available')
    search_fields = ('name',)
    readonly_fields = ('img_preview',)
    prepopulated_fields = {'slug': ('name',)}


class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'email', 'address', 'mobile', 'order_date', 'status')
    search_fields = ('customer',)

class SubscribedUsersAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'created_date')
    search_fields = ('email', 'name')


admin.site.register(Orders, OrderAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(SubscribedUser, SubscribedUsersAdmin)
