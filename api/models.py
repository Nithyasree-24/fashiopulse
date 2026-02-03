from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(unique=True, max_length=150)
    password = models.CharField(max_length=255)
    gender = models.CharField(max_length=10, blank=True, null=True) # Changed from 5 for enum flexibility
    size = models.CharField(max_length=5, blank=True, null=True)
    address = models.JSONField(blank=True, null=True) # Using JSON field for multiple addresses
    preferences = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'users'

class Clothing(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_image = models.CharField(max_length=255)
    product_name = models.CharField(max_length=150)
    product_category = models.CharField(max_length=100)
    combos = models.CharField(max_length=255, blank=True, null=True)
    product_description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=10) # Changed from 5
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    quantity = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'clothing'

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='user_id')
    product = models.ForeignKey(Clothing, on_delete=models.DO_NOTHING, db_column='product_id')
    quantity = models.IntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_address = models.TextField()
    payment_method = models.CharField(max_length=50, default='COD')
    payment_status = models.CharField(max_length=20, default='pending')
    order_status = models.CharField(max_length=20, default='placed')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'orders'

class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    product = models.ForeignKey(Clothing, on_delete=models.CASCADE, db_column='product_id')
    quantity = models.IntegerField(default=1)
    size = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'cart'
        unique_together = [['user', 'product', 'size']]

class Wishlist(models.Model):
    wishlist_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    product = models.ForeignKey(Clothing, on_delete=models.CASCADE, db_column='product_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'wishlist'
        unique_together = [['user', 'product']]
