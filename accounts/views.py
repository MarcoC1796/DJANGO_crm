from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from .models import *
from .forms import *
from .filters import OrderFilter
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

    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs
    
    return render(request, 'accounts/customer.html',
    {
        'customer':customer,
        'orders':orders,
        'orders_count': orders_count,
        'myFilter': myFilter
    })

def createOrder(request, pk):
    # Parent and child models with allowed fields
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=5) 
    customer = Customer.objects.get(id=pk)
    formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)
    if request.method == 'POST':
        # print('Printing POST:', request.POST)
        formset = OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')
    return render(request, 'accounts/order_form.html', {
        "formset": formset
    })

def updateOrder(request, pk):

    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)

    if request.method == 'POST':
        # print('Printing POST:', request.POST)
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')
    return render(request, 'accounts/order_form.html',{
        'form': form
    })

def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('/')

    return render(request, 'accounts/delete.html', {
        'item': order
    })