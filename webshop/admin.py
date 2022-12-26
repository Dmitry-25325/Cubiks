from django import forms
from django.contrib import admin
from .models import *
from django_admin_json_editor import JSONEditorWidget

# Schema for json field in products. For json editor.
DATA_SCHEMA = {
    'type': 'object',
    'title': 'Data',
    'properties': {
    },
}

class JSONModelAdminForm(forms.ModelForm):
    """ Class form for json editor """
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'characteristics': JSONEditorWidget(DATA_SCHEMA, collapsed=False),
        }

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """ Registers Category model to admin """

    list_display = ['category_name', 'category_slug']
    prepopulated_fields = {'category_slug': ('category_name', )}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """ Registers Product model to admin """

    list_display = ['product_name', 'product_slug', 'product_price', 'product_is_aviable', 'product_created', 'product_updated', 'product_image']
    list_filter = ['product_category', 'product_is_aviable', 'product_created', 'product_updated']
    list_editable = ['product_price', 'product_is_aviable']
    prepopulated_fields = {'product_slug': ('product_name',)}
    form = JSONModelAdminForm


@admin.register(ProductReview)
class ReviewAdmin(admin.ModelAdmin):
    """ Registers Review model to admin """

    list_display = ['product', 'author', 'date_published']
    list_filter = ['product', 'date_published']


@admin.register(UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    """ Registers UserInfo model to admin """

    list_display = ['user', 'purchased_items']