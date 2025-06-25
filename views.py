# from django.errors import messages
from django.db import IntegrityError
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages 
from .models import Cart, CartItem, Customer, Restaurant, Item
from .models import Customer

import razorpay
from django.conf import settings
from django.contrib.auth import authenticate, login, logout


# Create your views here.
def index(request):
    return render(request, 'delivery/index.html')

def open_signin(request):
    return render(request, 'delivery/signin.html')

def open_signup(request):
    return render(request, 'delivery/signup.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')

        try:
            Customer.objects.get(username = username)
            return HttpResponse("Duplicate username!")
        except:
            Customer.objects.create(
                username = username,
                password = password,
                email = email,
                mobile = mobile,
                address = address,
            )
    return render(request, 'delivery/signin.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

    try:
        Customer.objects.get(username = username, password = password)
        if username == 'admin':
            return render(request, 'delivery/admin_home.html')
        else:
            restaurantList = Restaurant.objects.all()
            return render(request, 'delivery/customer_home.html',{"restaurantList" : restaurantList, "username" : username})

    except Customer.DoesNotExist:
        return render(request, 'delivery/fail.html')
    
def open_add_restaurant(request):
    return render(request, 'delivery/add_restaurant.html')

def add_restaurant(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        picture = request.POST.get('picture')
        cuisine = request.POST.get('cuisine')
        rating = request.POST.get('rating')
        
        try:
            Restaurant.objects.get(name = name)
            return HttpResponse("Duplicate restaurant!")
        except:
            Restaurant.objects.create(
                name = name,
                picture = picture,
                cuisine = cuisine,
                rating = rating,
            )
    return render(request, 'delivery/admin_home.html')

def open_show_restaurant(request):
    restaurantList = Restaurant.objects.all()
    return render(request, 'delivery/show_restaurant.html',{"restaurantList" : restaurantList})

def open_update_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    return render(request, 'delivery/update_restaurant.html', {"restaurant" : restaurant})

def update_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        picture = request.POST.get('picture')
        cuisine = request.POST.get('cuisine')
        rating = request.POST.get('rating')
        
        restaurant.name = name
        restaurant.picture = picture
        restaurant.cuisine = cuisine
        restaurant.rating = rating

        restaurant.save()

    restaurantList = Restaurant.objects.all()
    return render(request, 'delivery/show_restaurant.html',{"restaurantList" : restaurantList})

def delete_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    restaurant.delete()


    restaurantList = Restaurant.objects.all()
    return render(request, 'delivery/show_restaurant.html',{"restaurantList" : restaurantList})

def open_update_menu(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    itemList = restaurant.items.all()

    
    # return render(request, 'delivery/update_menu.html',{"restaurant" : restaurant})
    return render(request, 'delivery/update_menu.html',{"itemList" : itemList, "restaurant" : restaurant})



def update_menu(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        vegeterian = request.POST.get('vegeterian') == 'on'
        picture = request.POST.get('picture')
        
        try:
            Item.objects.get(name = name)
            return HttpResponse("Duplicate Item!")
        except:
            Item.objects.create(
                restaurant = restaurant,
                name = name,
                description = description,
                price = price,
                vegeterian = vegeterian,
                picture = picture,
            )

    return render(request, 'delivery/admin_home.html')


def view_menu(request, restaurant_id, username):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    itemList = restaurant.menu_items.all().order_by('name') # Filter items by restaurant
    context = {
        'username': username,
        'restaurant': restaurant,
        'itemList': itemList,
    }
    return render(request, 'delivery/customer_menu.html', context)


    # restaurant = Restaurant.objects.get(id = restaurant_id)
    # itemList = restaurant.items.all()
    
    # #itemList = Item.objects.all()
    # return render(request, 'delivery/customer_menu.html',{"itemList" : itemList, "restaurant" : restaurant, "username":username})


def add_to_cart(request, item_id, username):
    # item = Item.objects.get(id = item_id)
    # customer = Customer.objects.get(username = username)

    # cart, created = Cart.objects.get_or_create(customer = customer)

    # cart.items.add(item)

    # return HttpResponse('added to cart')
    item = get_object_or_404(Item, id=item_id)
    
    try:
        user_obj = request.user  
        if not user_obj.is_authenticated:
            messages.error(request, "You must be logged in to add items to cart.")
            return redirect('signin')
        
    except AttributeError:
        user_obj = get_object_or_404(Customer, username=username)
        
    try:
        cart, created = Cart.objects.get_or_create(user=user_obj)
    
    except IntegrityError:
        cart = Cart.objects.get(user=user_obj)
        
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        menu_item=menu_item,
        defaults={'quantity': 1}
    )
    
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
        
    messages.success(request, f"{menu_item.item} added to cart!")
    return redirect('view_menu', restaurant_id=menu_item.restaurant.id, username=username)
    

def show_cart(request, username):
    cart = None
    cart_items = []
    total_price = 0

    # 1. Get the User object. Prioritize request.user if authenticated.
    try:
        user_obj = request.user
        if not user_obj.is_authenticated:
            messages.error(request, "You must be logged in to view your cart.")
            return redirect('signin') # Or your login URL name
    except AttributeError:
        # Fallback for when request.user might not be correctly set up
        # This part assumes you always have a user with the given username
        user_obj = get_object_or_404(User, username=username)

    # 2. Try to get the cart for this user
    # Using .first() on a filter or trying get_object_or_404 for OneToOneField
    # get_object_or_404 will raise 404 if no cart, which is fine, or you can handle it
    # with a try-except Cart.DoesNotExist
    try:
        cart = Cart.objects.get(user=user_obj) # Use .get() since it's OneToOneField, will raise DoesNotExist if not found
    except Cart.DoesNotExist:
        # If no cart exists for the user, cart remains None (as initialized above)
        pass # No need to do anything, cart is already None and cart_items/total_price are empty

    if cart:
        cart_items = CartItem.objects.filter(cart=cart).select_related('menu_item')
        total_price = cart.total_price() # This method should work correctly

    context = {
        'username': username,
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'customer_cart.html', context)
    
    
    
    # customer = Customer.objects.get(username = username)
    # cart = Cart.objects.filter(customer=customer).first()
    # items = cart.items.all() if cart else []
    # total_price = cart.total_price() if cart else 0

    # return render(request, 'delivery/cart.html',{"itemList" : items, "total_price" : total_price, "username":username})
    
    
    # try:
    #     user_obj = request.user 
    #     if not user_obj.is_authenticated:
    #         messages.error(request, "You must be logged is to view your cart.")
    #         return redirect('signup')
    
    # except AttributeError:
    #     user_obj = get_object_or_404(Customer, username=username)
    #     cart = Cart.objects.filter(user=user_obj).first()
        
    #     cart_items = []
    #     total_price = 0
        
    # if cart:
    #     cart_items = CartItem.objects.filter(cart=cart).select_related('menu_item')
    #     total_price = cart.total_price()
        
    # context = {
    #     'username': username,
    #     'cart_items': cart_items,
    #     'total_price': total_price,
    # }
    # return render(request, 'customer_cart.html', context)
        
            

def remove_from_cart(request, cart_item_id, username):
    cart_item_id = get_object_or_404(CartItem, id=cart_item_id)
    items = cart_item_id.menu_item.name
    cart_item_id.delete()
    messages.success(request, f"'{items}' removed from your cart.")
    return redirect('show_cart', username=username)

    


def checkout(request, username):
    # Fetch customer and their cart
    customer = get_object_or_404(Customer, username=username)
    cart = Cart.objects.filter(customer=customer).first()
    cart_items = cart.items.all() if cart else []
    total_price = cart.total_price() if cart else 0

    if total_price == 0:
        return render(request, 'delivery/checkout.html', {
            'error': 'Your cart is empty!',
        })

    # Initialize Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # Create Razorpay order
    order_data = {
        'amount': int(total_price * 100),  # Amount in paisa
        'currency': 'INR',
        'payment_capture': '1',  # Automatically capture payment
    }
    order = client.order.create(data=order_data)

    # Pass the order details to the frontend
    return render(request, 'delivery/checkout.html', {
        'username': username,
        'cart_items': cart_items,
        'total_price': total_price,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'order_id': order['id'],  # Razorpay order ID
        'amount': total_price,
    })


# Orders Page
def orders(request, username):
    customer = get_object_or_404(Customer, username=username)
    cart = Cart.objects.filter(customer=customer).first()

    # Fetch cart items and total price before clearing the cart
    cart_items = cart.items.all() if cart else []
    total_price = cart.total_price() if cart else 0

    # Clear the cart after fetching its details
    if cart:
        cart.items.clear()

    return render(request, 'delivery/orders.html', {
        'username': username,
        'customer': customer,
        'cart_items': cart_items,
        'total_price': total_price,
    })
