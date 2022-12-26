from django.views.generic import ListView
from .models import Category

class ShopViews(ListView):
    """Data mixin for shop views"""
    paginate_by = 9
    template_name = 'webshop/shop.html'

    def get_categories(self):
        "Returns all categories"
        return Category.objects.all()

    def min_product_price(self):
        "Gets min price of all product list"
        try:
            min_price = int(self.get_queryset().order_by('product_price').first().product_price)
        except AttributeError:
            min_price = self.request.GET.get('min_price')
        
        return min_price
    
    def max_product_price(self):
        """Gets max price of all product list"""
        try:
            max_price = int(self.get_queryset().order_by('product_price').last().product_price)
        except AttributeError:
            max_price = self.request.GET.get('max_price')
        
        return max_price