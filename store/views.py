from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm

from .models import Product, Cart, Order
from .forms import RegisterForm


def home(request):
    products = Product.objects.all()
    return render(request, 'index.html', {'products': products})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('home')


def products(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    return render(
        request,
        'product_detail.html',
        {'product': product}
    )


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('products')


@login_required
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)

    total = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    return render(
        request,
        'cart.html',
        {
            'cart_items': cart_items,
            'total': total,
        }
    )


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(
        Cart,
        id=item_id,
        user=request.user
    )

    item.delete()

    return redirect('cart')


@login_required
def update_cart(request, item_id):
    item = get_object_or_404(
        Cart,
        id=item_id,
        user=request.user
    )

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))

        if quantity > 0:
            item.quantity = quantity
            item.save()
        else:
            item.delete()

    return redirect('cart')


@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        return redirect('cart')

    total = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,
            total_price=total,
            status='Placed'
        )

        cart_items.delete()

        return render(
            request,
            'order_success.html',
            {'order': order}
        )

    return render(
        request,
        'checkout.html',
        {
            'cart_items': cart_items,
            'total': total,
        }
    )


@login_required
def order_history(request):
    orders = Order.objects.filter(
        user=request.user
    ).order_by('-order_date')

    return render(
        request,
        'order_history.html',
        {'orders': orders}
    )