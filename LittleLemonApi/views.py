from django.shortcuts import render
from django.http import JsonResponse
from .serializers import CategorySerializer, MenuItemSerializer, CartSerializer, OrderSerializer, OrderItemSerializer, GroupSerializer, UserSerializer
from .models import Category, MenuItem, Cart, Order, OrderItem
from rest_framework import generics
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from rest_framework import viewsets
from django.contrib.auth.models import Group, User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import user_passes_test

# Create your views here.
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def MenuItemsView(request):
    if request.method == 'GET':
        menu_items = MenuItem.objects.all()
        serializer = MenuItemSerializer(menu_items, many=True)
        return Response(serializer.data, status=200)

    elif request.method == 'POST':
        if not request.user.groups.filter(name='manager').exists():
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET', 'PUT', 'DELETE', 'POST'])
@permission_classes((IsAuthenticated,))
def SingleMenuItemView(request, pk=None):
    try:
        menu_item = MenuItem.objects.get(pk=pk)
    except MenuItem.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = MenuItemSerializer(menu_item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        if not request.user.groups.filter(name='manager').exists():
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        serializer = MenuItemSerializer(menu_item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if not request.user.groups.filter(name='manager').exists():
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        menu_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    elif request.method == 'POST':
        if not request.user.groups.filter(name='manager').exists():
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET', 'POST', 'DELETE'])
@permission_classes((IsAuthenticated,))
def manager_users(request):
    if not request.user.groups.filter(name='manager').exists():
            return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == 'POST':
        # handle user creation
        username = request.data.get('username')
        password = request.data.get('password')
        user = User.objects.create_user(username=username, password=password)
        group = Group.objects.get(name='manager')
        user.groups.add(group)
        return Response({'message': 'User created successfully.'}, status=status.HTTP_201_CREATED)

    # handle user retrieval
    manager_group = Group.objects.get(name='manager')
    users = manager_group.user_set.all()
    data = [{'id': user.id, 'username': user.username} for user in users]
    return Response(data)


@api_view(['GET', 'DELETE'])
def single_manager_user(request, pk):
    if not request.user.groups.filter(name='manager').exists():
            return Response(status=status.HTTP_403_FORBIDDEN)
            
    if request.method == 'DELETE':
        # handle user deletion
        user = get_object_or_404(User, id=pk)
        group = Group.objects.get(name='manager')
        user.groups.remove(group)
        
        return Response({'message': 'User deleted successfully.'}, status=status.HTTP_200_OK)

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes((IsAuthenticated,))
def delivery_crew(request):
    if not request.user.groups.filter(name='manager').exists():
            return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == 'POST':
        # handle user creation
        username = request.data.get('username')
        password = request.data.get('password')
        user = User.objects.create_user(username=username, password=password)
        group = Group.objects.get(name='delivery-crew')
        user.groups.add(group)
        return Response({'message': 'User created successfully.'}, status=status.HTTP_201_CREATED)

    # handle user retrieval
    manager_group = Group.objects.get(name='delivery-crew')
    users = manager_group.user_set.all()
    data = [{'id': user.id, 'username': user.username} for user in users]
    return Response(data)

@api_view(['GET', 'DELETE'])
def single_manager_user(request, pk):
    if not request.user.groups.filter(name='manager').exists():
            return Response(status=status.HTTP_403_FORBIDDEN)
            
    if request.method == 'DELETE':
        # handle user deletion
        user = get_object_or_404(User, id=pk)
        group = Group.objects.get(name='delivery-crew')
        user.groups.remove(group)
        
        return Response({'message': 'User deleted successfully.'}, status=status.HTTP_200_OK)

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart_view(request):
    user = request.user

    # check if the user belongs to either the manager or delivery-crew group
    manager_group = Group.objects.get(name='manager')
    delivery_crew_group = Group.objects.get(name='delivery-crew')
    if manager_group in user.groups.all() or delivery_crew_group in user.groups.all():
        return Response({"error": "Access denied"})

    if request.method == 'GET':
        # return current items in the cart for the current user
        items = Cart.objects.filter(user=user)
        item_data = []
        for item in items:
            item_data.append({
                'menuitem': item.menuitem.title,
                'quantity': item.quantity,
                'unit_price': item.unit_price
            })
        return Response({"cart_items": item_data})

    if request.method == 'POST':
        # add menu item to the cart
        menuitem_id = request.data.get('menuitem_id')
        quantity = request.data.get('quantity')
        menu_item = MenuItem.objects.get(id=menuitem_id)
        unit_price = menu_item.price

        cart_item, created = Cart.objects.get_or_create(
            user=user,
            menuitem=menu_item,
            defaults={'quantity': quantity, 'unit_price': unit_price}
        )
        

        if not created:
            # update the existing cart item
            int_quantity = int(quantity)
            cart_item.quantity += int_quantity
            cart_item.save()
            return Response({"message": "Menu item added to cart successfully"})

    if request.method == 'DELETE':
        Cart.objects.filter(user=user).delete()
        return Response({"message": "Menu item deleted from cart successfully"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_orders(request):
    if request.method == 'GET':
        user = request.user
        
        if not user.groups.filter(name__in=['manager', 'delivery-crew']).exists():
            orders = Order.objects.filter(user=user)
            order_items = OrderItem.objects.filter(order=user)

            order_data = []
            for order in orders:
                order_items = OrderItem.objects.filter(order=user)
                order_item_data = []
                for order_item in order_items:
                    order_item_data.append({
                        'user': order_item.order.username,
                        'menu-item': order_item.menuitem.title,
                        'quantity': order_item.quantity,
                        'unit-price': order_item.unit_price,
                        'price': order_item.price
                    })
                order_data.append({
                    'id': order.id,
                    'user': order.user.username,
                    'delivery-crew': order.delivery_crew.username,
                    'status': order.status,
                    'total': order.total,
                    'date': order.date,
                    'order_items': order_item_data
                })

            return Response({'orders': order_data})
        

    if request.method == 'POST':
        user = request.user
        if not user.groups.filter(name__in=['manager', 'delivery-crew']).exists():
            # Get current cart items for this user
            current_cart_items = Cart.objects.filter(user=user)

            # Create a new order for this user
            new_order = Order.objects.create(user=user)

            # Add current cart items to the order items table
            for cart_item in current_cart_items:
                OrderItem.objects.create(order=new_order, product=cart_item.product, quantity=cart_item.quantity, price=cart_item.price)

            # Delete all items from the cart for this user
            Cart.objects.filter(user=user).delete()

            return Response({'success': 'Order created successfully'})
        else:
            return Response({'error': 'Access denied: User is not authorized'})

        





