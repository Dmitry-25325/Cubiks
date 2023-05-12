from django.shortcuts import redirect, render, get_object_or_404
from .models import Category, Product, ProductReview, UserInfo
from django.views.generic import ListView, TemplateView, CreateView, FormView
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout, login
from .forms import UserRegisterForm, UserLoginForm, ReviewForm
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.models import User
from random import shuffle
from .utils import ShopViews


class Home(TemplateView):
    """ Home view """
    template_name = 'webshop/home.html'    


class MainPage(ListView):
    """ Main page view """
    template_name = 'webshop/main_page.html'
    model = Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_products'] = self.model.objects.order_by('-id')[:10]

        return context


class ShopPage(ShopViews):
    """Main shop view"""
    context_object_name = 'products'
    
    def get_queryset(self):
        return Product.objects.filter(product_is_aviable=True)


class CategoryPage(ShopViews):
    """ View for shop page with selected category """
    model = Product
    context_object_name = 'products'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context

    def get_queryset(self):
        return self.model.objects.filter(product_category=self.get_category())
    
    def get_category(self):
        return get_object_or_404(Category, category_slug=self.kwargs['category_slug'])


class ProductFilter(ShopViews):
    """ Filter view"""
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.get_category:
            context['category'] = self.get_category()
        
        return context

    def get_queryset(self):
        products = self.filter_products(category=self.get_category())
        
        return products
    
    def filter_products(self, category):
        """ Main filter function """
        sort_by = self.request.GET.get('sort_by')
        min_price = self.request.GET.get('min_price', 0)
        max_price = self.request.GET.get('max_price', 9999999)

        if sort_by:
            product_list = Product.objects.all().order_by(sort_by)
        else:
            product_list = Product.objects.all()

        if category:
            product_list = product_list.filter(
                product_category=category
                )

        if min_price:
            product_list = product_list.filter(
                product_price__gte=min_price,
            )

        if max_price:
            product_list = product_list.filter(
                product_price__lte=max_price,
            )

        return product_list

    def get_category(self):
        """ Gets category from GET data """
        if self.request.GET.get('category'):
            return get_object_or_404(Category, category_slug=self.request.GET.get('category'))
        else:
            return None


class ProductPage(FormView):
    """ Product's view """
    model = ProductReview
    context_object_name = "product"
    template_name = 'webshop/product_page.html'
    form_class = ReviewForm
    success_url = reverse_lazy('webshop:product_page')

    def form_valid(self, form):
        """ Creates reviews """
        if not self.user_has_review() and self.user_is_allowed_to_comment():
            f = form.save(commit=False)
            f.author = self.request.user
            f.product = self.get_product()
            f.save()        
        
        return HttpResponseRedirect(self.get_product().get_absolute_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.get_product()
        context['related_products'] = self.get_related_products()
        context['reviews'] = self.get_product_reviews()
        return context 

    def get_product(self):
        """ Gets product object"""
        return get_object_or_404(Product, product_slug=self.kwargs['product_slug'])
    
    def get_product_category(self):
        """ Gets product's category object """
        return get_object_or_404(Category, category_slug=self.kwargs['category_slug'])

    def get_related_products(self):
        """ Gets related products """
        product = self.get_product()

        related_products = Product.objects.filter(product_category=product.product_category,
                                                  product_price__lte=float(product.product_price) * 1.15,
                                                  product_price__gte=float(product.product_price) * 0.85
                                                  ).exclude(product_slug=product.product_slug)[:3]
        
        # If there are no related products, then returns them using a simpler algorithm
        if not related_products:
            related_products = Product.objects.filter(product_category=product.product_category
                                                      ).exclude(product_slug=product.product_slug)[:3]

        shuffle(related_products)

        return related_products

    def get_product_reviews(self):
        """ Returns all product reviews """
        return ProductReview.objects.filter(product=self.get_product())

    def user_has_review(self):
        """ Checks if user has a review on this product """
        reviews_authors = list(self.get_product_reviews().values_list('author', flat=True))
        
        if not reviews_authors:
            reviews_authors = (None, )

        return self.request.user.id in reviews_authors

    def user_is_allowed_to_comment(self):
        """ Allows user to buy product if he bought it"""
        if self.request.user.is_authenticated:
            try: 
                user_info = UserInfo.objects.get(user=self.request.user.id)
            except UserInfo.DoesNotExist:
                user_info = UserInfo()
                user_info.user = self.request.user 
                user_info.save()

            return self.get_product().product_slug in user_info.purchased_items['purchased_items']
            
        else:
            return False
            

class RegisterView(CreateView):
    """ Register view """
    template_name = 'webshop/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('webshop:main_page')
    
    def form_valid(self, form):
        """ Saves registered user """
        user = form.save()
        login(self.request, user)

        return redirect('webshop:main_page')


class LoginUser(LoginView):
    """ Login view"""
    form_class = UserLoginForm
    template_name = 'webshop/login.html'
    
    def get_success_url(self):
        return '/main'


class UserProfile(TemplateView):
    """ User profile view """
    template_name = 'webshop/profile.html'

    def get_user(self):
        """ Gets user from kwargs """
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_userinfo(self):
        """ Gets object of UserInfo model with requested user"""
        user = self.get_user()

        try: 
            user_info = UserInfo.objects.get(user=user.id)
        except UserInfo.DoesNotExist:
            user_info = UserInfo()
            user_info.user = user 
            user_info.save()

        return user_info
    
    def get_purchased_items(self):
        """ Gets all purchased items from user from json field """
        try:
            purchased_items = self.get_userinfo().purchased_items['purchased_items']
        except KeyError:
            return None

        items = Product.objects.filter(product_slug__in=purchased_items)

        return items


def logout_user(request):
    """ Simple logout view """
    logout(request)
    return redirect('webshop:login')


def remove_review(request):
    """ Removes selected review """
    review_id = request.POST.get('review_id')
    
    if not review_id:
        return HttpResponseForbidden()

    review = get_object_or_404(ProductReview, id=review_id)
    review_product = review.product

    if review.author == request.user:
        review.delete()
    else:
        return HttpResponseForbidden()
    
    return HttpResponseRedirect(review_product.get_absolute_url())


def buy_product(request):
    """ Final view after user purchase. Adds purchased product to UserInfo. """
    if not request.user.is_authenticated:
        return HttpResponseForbidden()

    if request.method == 'POST':
        product = get_object_or_404(Product, product_slug=request.POST.get('product', None))

        try: 
            user_info = UserInfo.objects.get(user=request.user)
        except UserInfo.DoesNotExist:
            user_info = UserInfo()
            user_info.user = request.user
            user_info.save()

        purchased_items = user_info.purchased_items.get('purchased_items', None)

        if not purchased_items:
            user_info.purchased_items = {'purchased_items': [product.product_slug, ]}
        elif product.product_slug in purchased_items:
            pass
        else:
            purchased_items.append(product.product_slug)
            user_info.purchased_items['purchased_items'] = purchased_items
        
        user_info.save()

        context = {
            'item': product,
            'quantity': request.POST.get('quantity', 1),
        }

        return render(request, 'webshop/buy_item.html', context=context)
    
    else:
        return HttpResponseForbidden()
