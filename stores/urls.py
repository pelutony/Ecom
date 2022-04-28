from django.urls import URLPattern, path

from . import views

urlpatterns=[
    path('',views.index,name='index'),
    path('category/',views.category,name='category'),
    path('singleproduct/<slug:slug>/',views.singleproduct,name='singleproduct'),
    path('addtocart/<int:id>/',views.addtocart,name='addtocart'),
    path('mycart/',views.mycart,name='mycart'),
    path('manageCart/<int:id>/',views.manageCart,name='manageCart'),
    path('emptyCart/',views.emptyCart,name='emptyCart'),
    path('checkout/',views.checkout,name='checkout'),
    path('register/',views.register,name='register'),
    path('loginuser/',views.loginuser,name='loginuser'),
    path('logout/',views.logoutuser,name='logout'),


    path('profile/',views.profile,name='profile'),
    path('order-detail/<int:id>/',views.orderDetails,name='order-detail'),
    path('search/',views.search,name='search'),

    
    path('profile/', views.profile, name='profile'),
    path('order-detail/<int:id>/',views.orderDetails,name='order-detail'),

    path('transfer/',views.transferPage,name='transfer'),
    path('payment/<int:id>/',views.paymentPage,name='payment'),
    path('<str:ref>/',views.verify_payment,name='verify-payment'),

    
]

