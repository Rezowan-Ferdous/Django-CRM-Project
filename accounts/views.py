from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.contrib import messages

from django.contrib.auth.decorators import login_required

from . import urls

from .decorators import unauthenticated_user,allowed_users,admin_only
from django.forms import inlineformset_factory ,formset_factory# multiple form within one form
from django.urls import NoReverseMatch, reverse
from .models import *
from .forms import OrderForm,CreateUserForm,CustomerForm
from .filters import *

# Create your views here.
@unauthenticated_user
def registerPage(request):
	form = CreateUserForm()
	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():
			user=form.save()

			username = form.cleaned_data.get('username')
			group=Group.objects.get(name='customer')
			user.groups.add(group)
			Customer.objects.create(
			user=user,
			)
			messages.success(request, 'Account was created for ' + username)

			return redirect('accounts:login')


	context = {'form':form}
	return render(request, 'accounts/register.html', context)

@unauthenticated_user
def loginPage(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password =request.POST.get('password')

		user = authenticate(request, username=username, password=password)

		if user is not None:
			login(request, user)
			return redirect('accounts:home')
		else:
			messages.info(request, 'Username OR password is incorrect')

	context = {}
	return render(request, 'accounts/login.html', context)

def logoutUser(request):
	logout(request)
	return redirect('accounts:login')


@login_required(login_url='accounts:login')
# @allowed_users(allowed_roles=['admin'])
@admin_only
def home(request):
	orders = Order.objects.all()
	customers = Customer.objects.all()

	total_customers = customers.count()

	total_orders = orders.count()
	delivered = orders.filter(status='delivered').count()
	pending = orders.filter(status='pending').count()

	context = {'orders':orders, 'customers':customers,
	'total_orders':total_orders,'delivered':delivered,
	'pending':pending }

	return render(request, 'accounts/dashboard.html', context)

# @login_required(login_url='login')
@login_required(login_url='accounts:login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
	orders = request.user.customer.order_set.all()
	total_orders = orders.count()
	delivered = orders.filter(status='delivered').count()
	pending = orders.filter(status='pending').count()
	# f"total orders{total_orders} pending {pending} delivered {delivered} "
	context={'orders':orders,
	'total_orders':total_orders,'delivered':delivered,
	'pending':pending,}
	return render(request,'accounts/user.html',context)

@login_required(login_url='accounts:login')
@allowed_users(allowed_roles=['customer'])

def accountSettings(request):
	customer=request.user.customer
	form=CustomerForm(instance=customer)
	if request.method=='POST':
		form=CustomerForm(request.POST,request.FILES,instance=customer)
		if form.is_valid():
			form.save()

	context={'form':form}
	return render(request,'accounts/account_settings.html',context)
# def home(request):
#     orders=Order.objects.all()
#     customers=Customer.objects.all()
#     total_customer=customers.count()
#     total_orders= orders.count()
#     delivered=orders.filter(status='delivered').count()
#     pending=orders.filter(status='pending').count()
#     context={
#     'orders':orders,
#     'customers':customers,
#     'total_orders':total_orders,
#     'total_customer':total_customer,
#     'pending':pending,
#     'delivered':delivered,
#     }
#     return render(request,'accounts/dashboard.html',context)
@login_required(login_url='accounts:login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    products=Product.objects.all()
    context={
    'products':products,
    }
    return render(request,'accounts/products.html',context)

@login_required(login_url='accounts:login')
@allowed_users(allowed_roles=['admin'])
def customer(request, pk_test):
    customer=Customer.objects.get(id=pk_test)
    orders=customer.order_set.all()
    order_count=orders.count()
    myFilter=OrderFilter(request.GET,queryset=orders)
    orders =myFilter.qs
    context={'customer': customer,
    'orders':orders,
    'myFilter':myFilter}

    return render(request,'accounts/customer.html',context)

@login_required(login_url='accounts:login')
@allowed_users(allowed_roles=['admin'])
def createOrder(request,pk):
    OrderFormSet=inlineformset_factory(Customer,Order, fields=('product','status'))
        #parent child
    customer=Customer.objects.get(id=pk)
    formset=OrderFormSet(queryset=Order.objects.none(),instance=customer)
    # form=OrderForm(initial={'customer':customer})

    if request.method == "POST":
        # print("request :",request.POST)
        form=OrderForm(request.POST)
        formset=OrderFormSet(request.POST,instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')
    context={'form':formset}
    return render(request,'accounts/order_form.html',context)

@login_required(login_url='accounts:login')
@allowed_users(allowed_roles=['admin'])

def updateOrder(request,pk):
    # OrderFormSet=formset_factory(Order)
    #     #parent child
    # customer=Customer.objects.get(id=pk)
    order=Order.objects.get(id=pk)
    # OrderFormSet=inlineformset_factory(Customer,Order, fields=('product','status'))
    form=OrderForm(instance=order)
    # formset=OrderFormSet(initial=[{'customer':customer,}])

    if request.method == "POST":
        form=OrderForm(request.POST,instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')

    context={'form':form}
    return render(request,'accounts/order_form.html',context)

@login_required(login_url='accounts:login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request,pk):
    order=Order.objects.get(id=pk)
    if request.method== "POST":
        order.delete()
        return redirect('/')

    context={'item':order}
    return render(request,'accounts/delete.html',context)
