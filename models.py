# from django.db import models
# from django.contrib.auth.models import User


# # Create your models here.
# class Customer(models.Model):
#     username = models.CharField(max_length=20)    
#     password = models.CharField(max_length=20)
#     email = models.CharField(max_length=20)
#     mobile = models.CharField(max_length=20)
#     address = models.CharField(max_length=20)
    
#     def __str__(self):
#         return f"Profile for {self.user.username}"

# class Restaurant(models.Model):
#     name = models.CharField(max_length = 255)
#     picture = models.URLField(max_length = 300,blank=True, null=True, default='https://designshack.net/wp-content/uploads/Free-Simple-Restaurant-Logo-Template.jpg')
#     cuisine = models.CharField(max_length = 200, blank=True)
#     rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
#     def __str__(self):
#         return self.name
    

# class Item(models.Model):
#     restaurant = models.ForeignKey(Restaurant, on_delete = models.CASCADE, related_name = "items")
#     name = models.CharField(max_length = 20)
#     description = models.CharField(max_length = 200)
#     price = models.FloatField()
#     vegeterian = models.BooleanField(default=False)
#     picture = models.URLField(max_length = 400, default='https://www.indiafilings.com/learn/wp-content/uploads/2024/08/How-to-Start-Food-Business.jpg')
        
        
# class Cart(models.Model):
#     customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
#     # items = models.ManyToManyField("Item", related_name="carts")
#     items = models.ManyToManyField(
#         Item)
    
#     def total_price(self):
#         # return sum(item.price for item in self.item.all())
#         total = sum(cart_item.menu_item.price * cart_item.quantity for cart_item in self.items.all())
#         return total
    
#     def __str__(self):
#         return f"Cart for {self.customer.name}"
    
    
# class CartItem(models.Model):
#     # Set related_name to 'items'
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
#     menu_item = models.ForeignKey(Item, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)
    
#     def __str__(self):
#         return f"{self.quantity} x {self.menu_item.name} in {self.cart.user.username}'s cart"
    
#     def subtotal(self):
#         return self.quantity * self.menu_item.price


# F:\Three\meal_buddy\delivery\models.py

from django.db import models
from django.contrib.auth.models import User # Correctly use Django's built-in User model

# 1. Restaurant Model (Looks mostly good, adjusted max_length for consistency)
class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    picture = models.URLField(max_length=300, blank=True, null=True, default='https://designshack.net/wp-content/uploads/Free-Simple-Restaurant-Logo-Template.jpg')
    cuisine = models.CharField(max_length=100, blank=True) # Changed to 100 for common cuisines
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)

    def __str__(self):
        return self.name

# 2. MenuItem Model (Renamed from Item for clarity and consistency, used DecimalField for price)
class Item(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="menu_items") # Renamed related_name from "items" to "menu_items" to avoid clash, although it wasn't the main clash.
    name = models.CharField(max_length=100) # Increased max_length for item names
    description = models.TextField(blank=True) # Changed to TextField for longer descriptions
    price = models.DecimalField(max_digits=6, decimal_places=2) # IMPORTANT: Changed to DecimalField for prices
    vegeterian = models.BooleanField(default=False)
    picture = models.URLField(max_length=400, blank=True, null=True, default='https://www.indiafilings.com/learn/wp-content/uploads/2024/08/How-to-Start-Food-Business.jpg')

    def __str__(self):
        return self.name
    
class Customer(models.Model):
    username = models.CharField(max_length=20)    
    password = models.CharField(max_length=20)
    email = models.CharField(max_length=20)
    mobile = models.CharField(max_length=20)
    address = models.CharField(max_length=20)
    
    def __str__(self):
        return f"Profile for {self.user.username}"


# 3. Cart Model (Crucial changes here)
class Cart(models.Model):
    # Link Cart directly to Django's User model
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # REMOVED: items = models.ManyToManyField(Item)
    # This was the clashing field. The items in the cart are now ONLY managed via CartItem.
    # The CartItem's ForeignKey with related_name='items' will handle the relation.

    def total_price(self):
        # This method correctly iterates through CartItem objects via the reverse relationship
        # 'self.items.all()' works because of the related_name='items' in CartItem's ForeignKey
        total = sum(cart_item.menu_item.price * cart_item.quantity for cart_item in self.items.all())
        return total

    def __str__(self):
        # Access username directly from the linked User model
        return f"Cart for {self.user.username}"

# 4. CartItem Model (Adjusted to link to MenuItem and corrected __str__ method)
class CartItem(models.Model):
    # This remains correct, providing the 'items' reverse accessor on the Cart model
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    
    # Link to MenuItem (your 'Item' model)
    menu_item = models.ForeignKey(Item, on_delete=models.CASCADE) # Now linked to MenuItem

    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        # Correctly access username from the Cart's linked User
        return f"{self.quantity} x {self.menu_item.name} in {self.cart.user.username}'s cart"

    @property # Use @property decorator for methods that act like attributes
    def subtotal(self):
        return self.quantity * self.menu_item.price

# 5. Customer Model (Removed - You should use Django's built-in User model and extend it if needed)
# If you need extra customer fields (like address, mobile), create a Profile model linked to User:
class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    # Add other customer-specific fields here

    def __str__(self):
        return f"Profile for {self.user.username}"

