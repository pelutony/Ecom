import imp
from django.http import JsonResponse
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render 

from multiprocessing import context
from django.shortcuts import redirect, render
from stores.forms import CheckoutForm, CustomerRegister

from django.conf import settings

from . models import *
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q
# Create your views here.
def index(request):
    allproduct = Product.objects.order_by('-created_at')
    allcategory = Category.objects.all()
    context ={
        'show':allproduct,
        'category':allcategory
    }
    return render(request, 'stores/index.html', context)


def category(request):
    allcategory = Category.objects.all()
    context = {
        'category':allcategory
    }
    return render(request, 'stores/category.html',context)


def singleproduct(request,slug):
    singleproduct = Product.objects.get(slug=slug)
    singleproduct.view_count+=1
    singleproduct.save()
    context ={
        'show':singleproduct,
    }
    return render(request, 'stores/single-product.html', context)


def addtocart(request,id):
    # get the
    cart_product = Product.objects.get(id=id)
    # check if cart exists
    cart_id =request.session.get('cart_id', None)
    if cart_id:
        cart_item = Cart.objects.get(id=cart_id)
        this_product_in_cart =cart_item.cartproduct_set.filter(product=cart_product)
        # assign cart to user
        if request.user.is_authenticated and request.user.customer:
                cart_item.customer = request.user.customer
                cart_item.save()
                # end
        # checking if item exist in cart
        if this_product_in_cart.exists():
            cartproduct= this_product_in_cart.last()
            cartproduct.quantity += 1
            cartproduct.subtotal += cart_product.price
            cartproduct.save()
            messages.success(request, 'Item increase in cart')
        # new item in cart
        else:
            cartproduct = CartProduct.objects.create(
                cart=cart_item, product=cart_product, rate=cart_product.price,
                quantity=1, subtotal=cart_product.price
            )
            cart_item.total += cart_product.price
            cart_item.save()
            messages.success(request, 'Item added to cart')

    else:
        cart_item = Cart.objects.create(total=0)
        request.session['cart_id'] = cart_item.id
        cartproduct = CartProduct.objects.create(cart=cart_item, product = cart_product, rate =cart_product.price, quantity=1, subtotal=cart_product.price)
        cart_item.total +=cart_product.price
        cart_item.save()
        messages.success(request, 'New Item to cart')
    return redirect('index')



def mycart(request):
    cart_id = request.session.get('cart_id', None)
    if cart_id:
        cart = Cart.objects.get(id=cart_id)
        # assign cart to user
        if request.user.is_authenticated and request.user.customer:
            cart.customer = request.user.customer
            cart.save()
            # end
    else:
        cart = None
    context = {
        'cart':cart,
    }
    return render(request, 'stores/mycart.html',context)

# manage cart
def manageCart(request,id):
    action = request.GET.get('action')
    cart_obj = CartProduct.objects.get(id=id)
    cart = cart_obj.cart
    if action == 'inc':
        cart_obj.quantity += 1
        cart_obj.subtotal += cart_obj.rate
        cart_obj.save()
        cart.total += cart_obj.rate
        cart.save()
        messages.success(request, 'Item quantity increase in cart')
        
    elif action == 'dcr':
        cart_obj.quantity -= 1
        cart_obj.subtotal -= cart_obj.rate
        cart_obj.save()
        cart.total -= cart_obj.rate
        cart.save()
        messages.success(request, 'Item quantity decrease in cart')

        if cart_obj.quantity == 0:
            cart_obj.delete()
    elif action == 'rmv':
        cart.total -= cart_obj.subtotal
        cart.save()
        cart_obj.delete()
        messages.success(request, 'Item remove in cart') 
    else:
        pass
    return redirect('mycart')

def emptyCart(request):
    cart_id = request.session.get('cart_id', None)
    if cart_id:
        cart = Cart.objects.get(id=cart_id)
        # assign cart to user
        if request.user.is_authenticated and request.user.customer:
            cart.customer = request.user.customer
            cart.save()
            # end
        cart.cartproduct_set.all().delete()
        cart.total = 0
        cart.save()
        messages.success(request, 'All item in cart deleted') 
    return redirect('mycart')
         
# checkout
def checkout(request):
    cart_id = request.session.get('cart_id', None)
    cart_obj = Cart.objects.get(id=cart_id)
    form = CheckoutForm()

    # checkout authentication
    if request.user.is_authenticated and request.user.customer:
        pass
    else:
        return redirect('/loginuser/?next=/checkout/')

    # getting cart
    if cart_id:
        cart_obj = Cart.objects.get(id=cart_id)
        # assign cart to user
        if request.user.is_authenticated and request.user.customer:
            cart_obj.customer = request.user.customer
            cart_obj.save()
            # end
    else:
        cart_obj = None

    # form
    if request.method == 'POST':
        form = CheckoutForm(request.POST or None)
        if form.is_valid():
            form = form.save(commit=False)
            form.cart = cart_obj
            form.discount = 0
            form.subtotal = cart_obj.total
            form.total = cart_obj.total
            form.order_status = 'Order  Received'
            pay_mth = form.payment_method
            del request.session['cart_id']
            pay_mth = form.payment_method
            form.save()
            order = form.id
            if pay_mth == 'Paystack':
                return redirect('payment', id=order)
            elif pay_mth == 'Payment Transfer':
                return redirect('transfer')

            del request.session['cart_id']
            messages.success(request, 'Order have been placed successfully')
            return redirect('index')
        else:
            messages.success(request, 'No order have been placed')
            return redirect('index')

    context ={
        'cart':cart_obj,
        'form':form,
    }
    return render(request, 'stores/checkout.html',context) 
    

# customer register
def register(request):
    if request.user.is_authenticated:
        return redirect('index')
    form = CustomerRegister()
    if request.method == 'POST':
        form = CustomerRegister(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password2')
            if User.objects.filter(username= username).exists():
                messages.warning(request,'User already exist')
                return redirect('register')
            if User.objects.filter(email=email).exists():
                messages.warning(request, 'Email already exist')
                return redirect ('register')
            if password != password2:
                messages.warning(request,'Password not match')
                return redirect('register')
            user = User.objects.create_user(username,email,password)
            form = form.save(commit=False)
            form.user=user
            form.save()
            messages.success(request, 'Registration successful')
            if "next" in request.GET:
                next_url=request.GET.get("next")
                return redirect(next_url)
            else:
                return redirect('loginuser')


    context={
        'form':form
    }
    return render(request, 'stores/register.html',context)

def loginuser(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        users = authenticate(request, username = username, password = password)
        if users is not None:
            login(request, users)
            messages.error(request, 'User Login Successfully')
            if "next" in request.GET:
                next_url=request.GET.get("next")
                return redirect(next_url)
            else:
                return redirect('index')
        else:
            messages.error(request,'Username/ password not correct')
    return render(request, 'stores/login.html')

def logoutuser(request):
    logout(request)
    messages.success(request,'Logout successful')
    return redirect('index')


# profile
def profile(request):
    if request.user.is_authenticated and request.user.customer:
        pass
    else:
        return redirect ('/loginuser/?next=/profile/')
    customer = request.user.customer
    orders = Order.objects.filter(cart__customer = customer).order_by('-id')
    context ={
        'customer':customer,
        'orders':orders,

    }
    return render(request, 'stores/profile.html',context)

# order detail of customer
def orderDetails(request,id):
    if request.user.is_authenticated and request.user.customer:
        order = Order.objects.get(id=id)
        if request.user.customer != order.cart.customer:
            return redirect('profile')
        else:
            return redirect('/loginuser/?next=/profile/')
    orders = Order.objects.get(id=id)
    context = {
        'orders':orders,
    }
    return render(request, 'stores/orderdetail.html',context)

# search
def search(request):
    thekw = request.GET.get('keyword')
    results= Product.objects.filter(Q(title__icontains=thekw) | Q(description__icontains=thekw))
    context ={
        'results':results,
    }
    return render(request, 'stores/search.html',context )

####payment######
def transferPage(request):
    return render(request, 'stores/transfer.html')

def paymentPage(request,id):

    orders = Order.objects.get(id=id)

    context= {
        'order':orders,
        'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY
    }
    return render(request, 'stores/payment.html', context)

def verify_payment(request: HttpRequest, ref:str) -> HttpResponse:
    payment = get_object_or_404(Order, ref=ref)
    verified = payment.verify_payment()

    if verified:
        messages.success(request, 'Verification Successful')
    else:
        messages.error(request, 'Verification Failed')
    return redirect('profile')
