from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
from .models import User, Clothing, Order, Cart, Wishlist
from .serializers import UserSerializer, ClothingSerializer, OrderSerializer, CartSerializer, WishlistSerializer
from .ai_logic import parse_user_prompt_llm
import logging

logger = logging.getLogger(__name__)

class SignupView(APIView):
    def post(self, request):
        data = request.data.copy()
        if User.objects.filter(email=data['email']).exists():
            return Response({"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)
        data['password'] = make_password(data['password'])
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = User.objects.get(email=email)
            if check_password(password, user.password):
                serializer = UserSerializer(user)
                return Response({"message": "Login successful", "user": serializer.data}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class UserProfileView(APIView):
    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            for key in ['address', 'gender', 'size', 'name', 'preferences']:
                if key in request.data: setattr(user, key, request.data[key])
            user.save()
            return Response({"message": "Profile updated", "user": UserSerializer(user).data})
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class AIQueryView(APIView):
    def post(self, request):
        try:
            prompt = request.data.get('prompt')
            user_id = request.data.get('user_id')
            
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            
            user_context = {
                "name": user.name,
                "gender": user.gender,
                "size": user.size,
                "address": user.address,
                "preferences": user.preferences
            }
            
            extracted = parse_user_prompt_llm(prompt, user_context)
            print(f"DEBUG: AI Extracted for Order: {extracted}")
            
            msg = "I'm on it!"
            products_data = []
            
            intent = extracted.get('intent', 'search')
            action = extracted.get('action', 'list')

            # Fast-Path for generic/empty prompts
            if not prompt or any(x in prompt.lower() for x in ['everything', 'show all', 'catalog']):
                products = Clothing.objects.all()
                if user.gender:
                    if 'women' in user.gender.lower(): products = products.filter(gender__icontains='Women')
                    elif 'men' in user.gender.lower(): products = products.filter(gender__icontains='Men')
                
                products_data = ClothingSerializer(products, many=True).data
                final_products = [] if not prompt else products_data

                return Response({
                    "machine_readable_json": extracted,
                    "message": f"Welcome, {user.name}! I'm ready for your command." if not prompt else f"Here is our full collection curated for you.",
                    "products": final_products,
                    "user_preferences": {"gender": user.gender, "size": user.size}
                })

            # CORE QUERY ENGINE
            search_params = ['category', 'color', 'budget', 'product_name', 'gender', 'size']
            if intent == 'search' or any(extracted.get(p) for p in search_params):
                products = Clothing.objects.all()
                
                target_gender = extracted.get('gender') or user.gender
                if target_gender:
                    if 'women' in target_gender.lower(): products = products.filter(gender__icontains='Women')
                    elif 'men' in target_gender.lower(): products = products.filter(gender__icontains='Men')
                
                name_query = extracted.get('product_name')
                cat_query = extracted.get('category') or (user.preferences.get('preferred_category') if user.preferences else None)
                
                if name_query:
                    products = products.filter(
                        Q(product_name__icontains=name_query) | 
                        Q(product_description__icontains=name_query) |
                        Q(product_category__icontains=name_query)
                    )
                elif cat_query:
                    # Direct Category Match
                    cat_map = {
                        'bottoms': 'Bottom Wear', 'bottom wear': 'Bottom Wear', 
                        't-shirts': 'T-shirts', 'shirts': 'Shirts', 
                        'dresses': 'Dresses', 'tops': 'Tops', 'tps': 'Tops',
                        'hoodies': 'Hoodies', 'jackets': 'Jackets', 'kurtis': 'Kurtis', 'sarees': 'Sarees',
                        'ethnic': 'Ethnic Wear'
                    }
                    mapped_cat = cat_map.get(cat_query.lower(), cat_query)
                    products = products.filter(product_category__iexact=mapped_cat)

                if extracted.get('color'): 
                    products = products.filter(color__icontains=extracted['color'])
                if extracted.get('budget'): 
                    products = products.filter(price__lte=extracted['budget'])
                
                target_size = extracted.get('size') or user.size
                if target_size: 
                    products = products.filter(size__icontains=target_size)
                
                products_data = ClothingSerializer(products, many=True).data
                if not products_data:
                    msg = "No products match your exact request."
                else:
                    msg = f"I found {len(products_data)} items matching your exact specifications."

            if intent == 'product_view':
                msg = f"Opening product details for you..."
            elif intent == 'order' or intent == 'payment':
                msg = "Proceeding to checkout. Please confirm the details."
                if intent == 'payment' and extracted.get('payment_method'):
                    msg = f"Setting payment method to {extracted['payment_method']} and completing order..."

            return Response({
                "machine_readable_json": extracted,
                "message": msg,
                "products": products_data,
                "user_preferences": {"gender": user.gender, "size": user.size}
            })
        except Exception as e:
            print(f"CRITICAL AIQueryView Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class OrderCreateView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        product_id = request.data.get('product_id')
        payment_method = request.data.get('payment_method', 'COD')
        delivery_address = request.data.get('delivery_address')
        quantity = int(request.data.get('quantity', 1))
        order_size = request.data.get('size')
        
        try:
            user = User.objects.get(id=user_id)
            product = Clothing.objects.get(product_id=product_id)
            
            # Use provided delivery_address or fallback to user's first saved address
            final_address = delivery_address
            if not final_address:
                if isinstance(user.address, dict) and user.address:
                    final_address = list(user.address.values())[0]
                elif isinstance(user.address, str):
                    final_address = user.address
            
            if not final_address:
                return Response({"error": "Please add a delivery address first."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Calculate Total
            total_price = product.price * quantity
                
            order = Order.objects.create(
                user=user,
                product=product,
                quantity=quantity,
                total_amount=total_price,
                delivery_address=final_address,
                payment_method=payment_method,
                payment_status='paid' if payment_method != 'COD' else 'pending',
                order_status='placed'
            )
            
            return Response({
                "message": "Order Placed Successfully",
                "order_details": {
                    "order_id": order.order_id,
                    "product_name": product.product_name,
                    "product_size": order_size or product.size,
                    "product_image": product.product_image,
                    "quantity": order.quantity,
                    "price_per_item": str(product.price),
                    "total": str(order.total_amount),
                    "address": order.delivery_address,
                    "payment_method": order.payment_method
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class OrderListView(APIView):
    def get(self, request, user_id):
        try:
            orders = Order.objects.filter(user_id=user_id).order_by('-created_at')
            return Response(OrderSerializer(orders, many=True).data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class BulkOrderView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        items = request.data.get('items', [])
        payment_method = request.data.get('payment_method', 'COD')
        delivery_address = request.data.get('delivery_address')

        if not items:
            return Response({"error": "No items in cart"}, status=status.HTTP_400_BAD_REQUEST)
        if not delivery_address:
            return Response({"error": "Delivery address required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
            orders_created = []
            total_bulk_amount = 0

            for item in items:
                product = Clothing.objects.get(product_id=item['product_id'])
                qty = int(item.get('quantity', 1))
                amount = product.price * qty
                total_bulk_amount += amount

                order = Order.objects.create(
                    user=user,
                    product=product,
                    quantity=qty,
                    total_amount=amount,
                    delivery_address=delivery_address,
                    payment_method=payment_method,
                    payment_status='paid' if payment_method != 'COD' else 'pending',
                    order_status='placed'
                )
                orders_created.append(order.order_id)

            return Response({
                "message": "Bulk Order Placed Successfully",
                "bulk_details": {
                    "order_ids": orders_created,
                    "total_amount": str(total_bulk_amount),
                    "item_count": len(items)
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CancelOrderView(APIView):
    def post(self, request):
        order_id = request.data.get('order_id')
        try:
            order = Order.objects.get(order_id=order_id)
            if order.order_status in ['placed', 'processing']:
                order.order_status = 'cancelled'
                order.save()
                return Response({"message": f"Order #{order_id} has been cancelled successfully."})
            else:
                return Response({"error": f"Order cannot be cancelled in '{order.order_status}' status."}, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ==================== CART API VIEWS ====================

class GetCartView(APIView):
    """Get all cart items for a specific user"""
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cart_items = Cart.objects.filter(user_id=user_id).select_related('product')
            serializer = CartSerializer(cart_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Get cart error: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AddToCartView(APIView):
    """Add item to cart or update quantity if already exists"""
    def post(self, request):
        user_id = request.data.get('user_id')
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        size = request.data.get('size', 'M')
        
        if not user_id or not product_id:
            return Response({"error": "user_id and product_id are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Check if item already exists in cart
            cart_item, created = Cart.objects.get_or_create(
                user_id=user_id,
                product_id=product_id,
                size=size,
                defaults={'quantity': quantity}
            )
            
            if not created:
                # Update quantity if item already exists
                cart_item.quantity += quantity
                cart_item.save()
            
            serializer = CartSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Add to cart error: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateCartView(APIView):
    """Update cart item quantity or size"""
    def put(self, request):
        cart_id = request.data.get('cart_id')
        quantity = request.data.get('quantity')
        size = request.data.get('size')
        
        if not cart_id:
            return Response({"error": "cart_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cart_item = Cart.objects.get(cart_id=cart_id)
            
            if quantity is not None:
                cart_item.quantity = quantity
            if size is not None:
                cart_item.size = size
            
            cart_item.save()
            serializer = CartSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Update cart error: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RemoveFromCartView(APIView):
    """Remove specific item from cart"""
    def delete(self, request):
        cart_id = request.data.get('cart_id')
        
        if not cart_id:
            return Response({"error": "cart_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cart_item = Cart.objects.get(cart_id=cart_id)
            cart_item.delete()
            return Response({"message": "Item removed from cart"}, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Remove from cart error: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ClearCartView(APIView):
    """Clear all cart items for a user (used after checkout)"""
    def delete(self, request):
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            deleted_count, _ = Cart.objects.filter(user_id=user_id).delete()
            return Response({"message": f"Cart cleared. {deleted_count} items removed."}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Clear cart error: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ==================== WISHLIST API VIEWS ====================

class GetWishlistView(APIView):
    """Get all wishlist items for a specific user"""
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            wishlist_items = Wishlist.objects.filter(user_id=user_id).select_related('product')
            serializer = WishlistSerializer(wishlist_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Get wishlist error: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AddToWishlistView(APIView):
    """Add item to wishlist"""
    def post(self, request):
        user_id = request.data.get('user_id')
        product_id = request.data.get('product_id')
        
        if not user_id or not product_id:
            return Response({"error": "user_id and product_id are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            wishlist_item, created = Wishlist.objects.get_or_create(
                user_id=user_id,
                product_id=product_id
            )
            
            if not created:
                return Response({"message": "Item already in wishlist"}, status=status.HTTP_200_OK)
            
            serializer = WishlistSerializer(wishlist_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Add to wishlist error: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RemoveFromWishlistView(APIView):
    """Remove specific item from wishlist"""
    def delete(self, request):
        wishlist_id = request.data.get('wishlist_id')
        
        if not wishlist_id:
            return Response({"error": "wishlist_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            wishlist_item = Wishlist.objects.get(wishlist_id=wishlist_id)
            wishlist_item.delete()
            return Response({"message": "Item removed from wishlist"}, status=status.HTTP_200_OK)
        except Wishlist.DoesNotExist:
            return Response({"error": "Wishlist item not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Remove from wishlist error: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ToggleWishlistView(APIView):
    """Toggle wishlist status (add if not exists, remove if exists)"""
    def post(self, request):
        user_id = request.data.get('user_id')
        product_id = request.data.get('product_id')
        
        if not user_id or not product_id:
            return Response({"error": "user_id and product_id are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            wishlist_item = Wishlist.objects.filter(user_id=user_id, product_id=product_id).first()
            
            if wishlist_item:
                # Remove from wishlist
                wishlist_item.delete()
                return Response({"message": "Item removed from wishlist", "in_wishlist": False}, status=status.HTTP_200_OK)
            else:
                # Add to wishlist
                wishlist_item = Wishlist.objects.create(user_id=user_id, product_id=product_id)
                serializer = WishlistSerializer(wishlist_item)
                return Response({"message": "Item added to wishlist", "in_wishlist": True, "data": serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Toggle wishlist error: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
