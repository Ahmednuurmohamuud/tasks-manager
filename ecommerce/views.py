from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# ecommerce/views.py
from django.conf import settings
from django.shortcuts import render, get_object_or_404
import stripe
from .models import Product

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'ecommerce/product_list.html', {'products': products})


@login_required
def checkout(request, pk):
    product = get_object_or_404(Product, pk=pk)
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'inr',
                'product_data': {
                    'name': product.name,
                },
                'unit_amount': int(product.price * 100),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://127.0.0.1:8000/success/',
        cancel_url='http://127.0.0.1:8000/cancel/',
    )
    return render(request, 'ecommerce/checkout.html', {
        'session_id': session.id,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })


@login_required
def success(request):
    return render(request, 'ecommerce/success.html')


@login_required
def cancel(request):
    return render(request, 'ecommerce/cancel.html')


@login_required
def home(request):
    # Placeholder data - we'll later fetch this from the database
    context = {
        'user': request.user,
        'birthdays': [],   # List of upcoming birthdays
        'holidays': [],    # List of upcoming holidays
        'best_employees': []  # Best employees' list for the scrolling section
    }   
    return render(request, 'ecommerce/home.html', context)