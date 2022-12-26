from django.urls import path
from . import views

app_name = 'webshop'

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('main/', views.MainPage.as_view(), name='main_page'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('remove_review/', views.remove_review, name='remove_review'),
    path('buy/', views.buy_product, name='buy_product'),    
    path('filter/', views.ProductFilter.as_view(), name='filter'),
    path('shop/', views.ShopPage.as_view(), name='shop_page'),
    path('shop/<category_slug>', views.CategoryPage.as_view() , name='category_page'),
    path('shop/<category_slug>/<product_slug>', views.ProductPage.as_view(), name='product_page'),
    path('profile/<username>', views.UserProfile.as_view(), name='profile')
]
