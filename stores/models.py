from crypt import METHOD_BLOWFISH
import secrets
from django.db import models
from django.contrib.auth.models import User

from .paystack import paystack

# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    address = models.CharField(max_length=200, null =True,blank=True)
    registered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

class Category(models.Model):
    title =models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
	
    def __str__(self):
        return self.title

class Product(models.Model):
    title =models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products")
    price = models.PositiveIntegerField()
    discount_price = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField()
    warranty = models.CharField(max_length=200, null=True,blank=True)
    return_policy = models.CharField(max_length=200, null=True,blank=True)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True,blank=True)

    def __str__(self):
        return f'{self.title} ::: {self.category}'

class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,null=True,blank=True)
    total = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.customer} ::: {self.total}'


class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,null=True,blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rate = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.rate} ::: {self.quantity}'

OREDER_STATUS = (
	('Order Received','Order Received'),
	('Order Processing','Order Processing'),
	('On the way','On the way'),
	('Order Completed','Order Completed'),
	('Order Canceled','Order Canceled'),
	)

METHOD=(
	('Cash on Delivery','Cash on Delivery'),
	('Paystack','Paystack'),
	('Payment Transfer','Payment Transfer'),
)

class Order(models.Model):
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    ordered_by =models.CharField(max_length=200)
    shipping_address = models.CharField(max_length=200)
    mobile = models.CharField(max_length=11)
    email = models.EmailField(null=True,blank=True)
    discount = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    order_status = models.CharField(max_length=200, choices=OREDER_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
	
    payment_method= models.CharField(max_length=20, choices=METHOD, default='Cash on Delivery')
    payment_completed=models.BooleanField(default=False,null=True,blank=True)
    ref=models.CharField(max_length=20,null=True,blank=True)

    def __str__(self):
        return f'{self.order_status} ::: {str(self.id)}'
	
def save(self, *args **kwargs):
		while not self.ref:
			ref = secrets.token_urlsafe(50)
			obj_with_sm_ref=Order.objects.filter(ref=ref)
			if not obj_with_sm_ref:
				self.ref=ref                                                     
                super().save(*args, **kwargs)
def amount_value(self) -> int:
		return self.total * 100
def verify_payment(self):
		paystack = Paystack()
		status, result = paystack.verify_payment(self.ref, self.total)
		if status:
			if result['total']/100 == self.total:
				self.payment_completed=True
			self.save()
		if self.payment_completed:
			return True
		return False


	
	