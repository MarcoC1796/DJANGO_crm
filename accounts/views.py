from django.shortcuts import render
from django.http import HttpResponse
from .models import *
# Create your views here.

def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()

    total_customers = customers.count()

    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    return render(request, 'accounts/dashboard.html',
    {
        'orders':orders,
        'customers':customers,
        'total_orders': total_orders,
        'delivered': delivered,
        'pending': pending
    })

def products(request):
    products = Product.objects.all()
    return render(request, 'accounts/products.html', 
    {
        'products': products
    })

def customer(request, pk):
    customer = Customer.objects.get(pk=pk)
    orders = customer.order_set.all()
    orders_count = orders.count()

    return render(request, 'accounts/customer.html',
    {
        'customer':customer,
        'orders':orders,
        'orders_count': orders_count
    })

def createOrder(request):
    return render(request, 'accounts/order_form.html')