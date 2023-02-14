from django.urls import path,include
from . import views 
from rest_framework.routers import DefaultRouter


urlpatterns = [
    path('menu-items', views.MenuItemsView),
    path('menu-items/<int:pk>', views.SingleMenuItemView),
    path('groups/manager/users', views.manager_users),
    path('groups/manager/users/<int:pk>/', views.single_manager_user),
    path('groups/delivery-crew/users', views.delivery_crew),
    path('cart/menu-items', views.cart_view),
    path('orders', views.all_orders),
]
