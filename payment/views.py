from django.shortcuts import render, HttpResponseRedirect, redirect
from django.urls import reverse

from payment.forms import BillingAddressForm
from payment.models import BillingAddress
from order.models import Order, Cart

from django.contrib import messages

from django.contrib.auth.decorators import login_required

# for payment import ssl commerz
from sslcommerz_python.payment import SSLCSession
from decimal import Decimal
import socket

from django.views.decorators.csrf import csrf_exempt


@login_required
def checkout(request):
    saved_address = BillingAddress.objects.get_or_create(user=request.user)
    saved_address = saved_address[0]
    form = BillingAddressForm(instance=saved_address)
    if request.method == 'POST':
        form = BillingAddressForm(request.POST, instance=saved_address)
        if form.is_valid():
            form.save()
            form = BillingAddressForm(instance=saved_address)
            messages.info(request, "Shipping Address has been Saved!")

    order_qs = Order.objects.filter(user=request.user, ordered=False)
    order_items = order_qs[0].orderitems.all()
    order_total = order_qs[0].get_totals()
    context = {
        'form': form,
        'order_items': order_items,
        'order_total': order_total,
        'save_address': saved_address
    }
    return render(request, 'payment/checkout.html', context)


@login_required
def payment(request):
    saved_address = BillingAddress.objects.get_or_create(user=request.user)
    saved_address = saved_address[0]
    if not saved_address.is_fully_filled():
        messages.info(request, "please complete shipping address")
        return redirect('payment:checkout')

    if not request.user.profile.is_fully_filled():
        messages.info(request, "Please complete profile details!")
        return redirect('account:profile')

    # ssl commerz required process
    store_id = 'cleve6084e47685c74'
    store_pass = 'cleve6084e47685c74@ssl'
    mypayment = SSLCSession(sslc_is_sandbox=True, sslc_store_id=store_id,
                            sslc_store_pass=store_pass)

    status_url = request.build_absolute_uri(reverse('payment:complete'))

    mypayment.set_urls(success_url=status_url, fail_url=status_url,
                       cancel_url=status_url, ipn_url=status_url)

    order_qs = Order.objects.filter(user=request.user, ordered=False)
    order_items = order_qs[0].orderitems.all()
    order_items_count = order_qs[0].orderitems.count()
    order_total = order_qs[0].get_totals()
    mypayment.set_product_integration(total_amount=Decimal(order_total), currency='BDT', product_category='Mixed',
                                      product_name=order_items, num_of_item=order_items_count,
                                      shipping_method='Courier',
                                      product_profile='None')

    current_user = request.user

    mypayment.set_customer_info(name=current_user.profile.full_name, email=current_user.email,
                                address1=current_user.profile.address_1,
                                address2=current_user.profile.address_1, city=current_user.profile.city,
                                postcode=current_user.profile.zipcode, country=current_user.profile.country,
                                phone=current_user.profile.phone)

    mypayment.set_shipping_info(shipping_to=current_user.profile.full_name, address=saved_address.address,
                                city=saved_address.city, postcode=saved_address.zipcode,
                                country=saved_address.country)

    response_data = mypayment.init_payment()
    print(response_data)

    return redirect(response_data['GatewayPageURL'])


@csrf_exempt
def complete(request):
    if request.method == 'POST' or request.method == 'post':
        payment_data = request.POST
        status = payment_data['status']

        if status == 'VALID':
            val_id = payment_data['val_id']
            tran_id = payment_data['tran_id']
            messages.success(request, "Your Payment Completed Successfully!")
            return HttpResponseRedirect(reverse('payment:purchase', kwargs={'val_id': val_id, 'tran_id': tran_id}))
        elif status == 'FAILED':
            messages.warning(request, "Your Payment Failed Please try again!")

    context = {

    }
    return render(request, 'payment/complete.html', context)


@login_required
def purchase(request, val_id, tran_id):
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    order = order_qs[0]
    order.ordered = True
    order.orderId = tran_id
    order.paymentId = val_id
    order.save()
    cart_items = Cart.objects.filter(user=request.user, purchased=False)
    for item in cart_items:
        item.purchased = True
        item.save()
    return HttpResponseRedirect(reverse('payment:orders'))




@login_required
def order_view(request):
    try:
        orders = Order.objects.filter(user=request.user, ordered=True)
        context = {
            'orders': orders
        }

    except:
        messages.warning(request, "You don't have an active order!")
        return redirect('store:index')

    return render(request, 'payment/order.html', context)












