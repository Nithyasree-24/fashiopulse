from django.urls import path
from .views import (
    SignupView, LoginView, UserProfileView, AIQueryView, OrderCreateView, OrderListView, BulkOrderView, CancelOrderView,
    GetCartView, AddToCartView, UpdateCartView, RemoveFromCartView, ClearCartView,
    GetWishlistView, AddToWishlistView, RemoveFromWishlistView, ToggleWishlistView
)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/<int:user_id>/', UserProfileView.as_view(), name='profile'),
    path('ai-query/', AIQueryView.as_view(), name='ai-query'),
    path('order/', OrderCreateView.as_view(), name='order'),
    path('orders/<int:user_id>/', OrderListView.as_view(), name='order-list'),
    path('bulk-order/', BulkOrderView.as_view(), name='bulk-order'),
    path('cancel-order/', CancelOrderView.as_view(), name='cancel-order'),
    
    # Cart endpoints
    path('cart/', GetCartView.as_view(), name='get_cart'),
    path('cart/add/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/update/', UpdateCartView.as_view(), name='update_cart'),
    path('cart/remove/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('cart/clear/', ClearCartView.as_view(), name='clear_cart'),
    
    # Wishlist endpoints
    path('wishlist/', GetWishlistView.as_view(), name='get_wishlist'),
    path('wishlist/add/', AddToWishlistView.as_view(), name='add_to_wishlist'),
    path('wishlist/remove/', RemoveFromWishlistView.as_view(), name='remove_from_wishlist'),
    path('wishlist/toggle/', ToggleWishlistView.as_view(), name='toggle_wishlist'),
]
