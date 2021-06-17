import admin_thumbnails
from django.contrib import admin

from .models import Product, ProductGallery, ReviewModel, Variation


@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1


@admin.register(Product)
@admin_thumbnails.thumbnail('image')
class ProductAdmin(admin.ModelAdmin):
    '''Admin View for Product'''

    list_display = ('__str__', 'price', 'stock', 'is_available')
    list_filter = ('category', 'is_available')
    inlines = [ProductGalleryInline]


@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    '''Admin View for Variation'''

    list_display = ('__str__', 'variation_category', 'variation_value', 'timestamp', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value')


@admin.register(ReviewModel)
class ReviewModelAdmin(admin.ModelAdmin):
    '''Admin View for Product'''

    list_display = ('__str__', 'product', 'rating', 'status')


admin.site.register(ProductGallery)
