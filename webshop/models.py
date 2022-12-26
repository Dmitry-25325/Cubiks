from django.db import models
from django.urls import reverse, reverse_lazy
from django.conf import settings


class Category(models.Model):
    "Products category model"
    category_name = models.CharField(max_length=100, db_index=True, verbose_name="Category name")
    category_slug = models.SlugField(max_length=100, unique=True)
    
    class Meta:
        ordering = ('category_name',)
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self) -> str:
        return self.category_name

    def get_absolute_url(self):
        return reverse('webshop:category_page', args=[self.category_slug])


class Product(models.Model):
    "Product model"
    product_category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, verbose_name='Choose a category')
    
    product_name = models.CharField(max_length=255, db_index=True, verbose_name='Name')
    product_slug = models.SlugField(max_length=255, db_index=True)
    product_image = models.ImageField(upload_to='images/product_imgs/', blank=True, verbose_name='Image')
    product_description = models.TextField(blank=True, verbose_name='Description')
    product_price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Price')
    product_is_aviable = models.BooleanField(default=True, verbose_name='Availability')
    product_created = models.DateTimeField(auto_now_add=True)
    product_updated = models.DateTimeField(auto_now=True)
    characteristics = models.JSONField(default=dict)

    class Meta:
        ordering = ('product_name', )
        index_together = (('id', 'product_slug'), )
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self) -> str:
        return self.product_name

    def get_absolute_url(self):
        return reverse_lazy('webshop:product_page', args=[self.product_category.category_slug, self.product_slug])


class ProductReview(models.Model):
    "Review model"
    product = models.ForeignKey(Product, related_name='review', on_delete=models.CASCADE, verbose_name='Choose a product')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, verbose_name='Author')
    content = models.TextField(max_length=2048, verbose_name='Content')
    is_recommend = models.BooleanField(default=True, verbose_name='Will you recommend?')
    date_published = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ('date_published', )

    def __str__(self):
        return f"{self.product} {self.author}"


class UserInfo(models.Model):
    """ Extends base User model to save the products that the user has bought """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='User')
    purchased_items = models.JSONField(default=dict, verbose_name='Purchased Items')

    def __str__(self):
        return f"{self.user} info"

    class Meta:
        verbose_name = 'User Info'
        verbose_name_plural = 'Users Info'

