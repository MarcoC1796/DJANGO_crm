from django.shortcuts import render, redirect, reverse
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.forms import inlineformset_factory
from .models import *
from .forms import *
from .filters import OrderFilter
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .decorators import *

# Create your views here.
@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            group = Group.objects.get(name='customer')
            user.groups.add(group)
            Customer.objects.create(
                user=user
            )
            messages.success(request, 'Account was created for ' + username)
            return redirect(reverse('login'))
    return render(request, 'accounts/register.html', {
        'form': form
    })

@unauthenticated_user
def loginPage(request):
    if request.user.is_authenticated:
        return redirect(reverse('home'))
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(reverse('home'))
        else:
            messages.info(request, 'Username OR password is incorrect')

    return render(request, 'accounts/login.html', {

    })

def logoutUser(request):
    logout(request)
    return redirect(reverse('login'))

@login_required(login_url='login')
@admin_only
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

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
    orders = request.user.customer.order_set.all()
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()
    print('ORDERS: ',orders)
    return render(request, 'accounts/user.html', {
        'orders': orders,
        'total_orders': total_orders,
        'delivered': delivered,
        'pending': pending
    })

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)
    if request.method == "POST":
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
    return render(request, 'accounts/account_settings.html', {
        'form': form
    })

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()

    return render(request, 'accounts/products.html', 
    {
        'products': products
    })

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
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

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
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

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request, pk):

    order = Order.objects.get(id=pk)
    print(order)
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

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('/')

    return render(request, 'accounts/delete.html', {
        'item': order
    })