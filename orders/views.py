from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from carts.models import Cart, CartItem
from .models import Order, Payment, OrderProduct
from .forms import OrderForm
import datetime
import json
from store.models import Product



from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode , urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages , auth
from django.contrib.auth.decorators import login_required



# Create your views here.





def payments(request):
    body = json.loads(request.body)
    print(body)

    # in use to order number in conform the user and store the order variable 
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    # store transation details inside payment model 
    payment  = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method  = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],

    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()



    # Move the cart items to Order Product table 
    cart_items = CartItem.objects.filter(user=request.user)   # in cart item filter this items (in the following item are writtern in the down the line )
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id 
        orderproduct.product_id = item.product_id 
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id = item.id)   # in cart item fetch item id 
        product_variation = cart_item.variations.all()  # all variations are show 
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)  # in the id of product 
        orderproduct.variations.set(product_variation)  # variation of product variation 
        orderproduct.save()




        # Reduce the quantity of the sold product 
        product = Product.objects.get(id = item.product_id)
        product.stock -= item.quantity
        product.save()







    # clear the cart 
    CartItem.objects.filter(user=request.user).delete()


    # send order reciped email to consomer 

    mail_subject="Thank you for your order!"
    message = render_to_string('orders/order_recieved_email.html', {
        'user':request.user,
        'order':order,

                

        })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject,
                                message, 
                                to=[to_email])
    send_email.send()



    # send order number and transation id back to send data method via json response 
    data = {
        'order_number':order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)



    return render(request, 'orders/payments.html')






def place_order(request, total=0, quantity=0):
    current_user = request.user 


    # if the cart count is less then or equal to 0, then redirect back to shop 
    cart_items = CartItem.objects.filter(user = current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    
    tax = (2 * total) / 100
    grand_total = total + tax 


    

    if request.method == 'POST':
        form  = OrderForm(request.POST) 
        if form.is_valid():
            # store all the billing information inside Order Table 
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']

            data.order_total =  grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            # generate order number 
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime('%Y%m%d')  # year,month,date
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order':order,
                'cart_items':cart_items,
                'grand_total':grand_total,
                'total':total,
                'tax':tax,
            }

            return render(request, 'orders/payments.html', context)
            
        
        else:
            return redirect('checkout')





def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        
        payment = Payment.objects.get(payment_id=transID)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity


        context = {
            'order':order,
            'ordered_products':ordered_products,
            'order_number':order.order_number,
            'transID':payment.payment_id,
            'payment':payment,
            'subtotal':subtotal,
        }
        return render(request, 'orders/order_complete.html',context)
    
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
    


