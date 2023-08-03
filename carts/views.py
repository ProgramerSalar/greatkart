from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from store.models import Product
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist  
from store.models import Variation, VariationManager
from django.contrib.auth.decorators import login_required










# Create your views here.


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart




def add_cart(request, product_id):
    current_user = request.user
    product  = Product.objects.get(id=product_id)   # get the product 
    product_variation = []
    # if user is authenticated 
    if current_user.is_authenticated:
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                # print(key, value)
                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                    
                except:
                    pass




        

        is_cart_item_exists = CartItem.objects.filter(product=product,user=current_user).exists()  # check the product is exists or not
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product,user=current_user)  # exists in the cart the filter the product = product 
            # existing varations -> database
            # current varation -> product varation 
            # item_id -> database
            existing_varation_list = [] # product is append in the list 
            id = []  # create the empty list id -> 2
            for item in cart_item:
                existing_varation = item.variations.all()   # all product varations are show 
                existing_varation_list.append(list(existing_varation))   # varations are append in the list of existing_varation_list 
                id.append(item.id) # append the item in id -> 2 

            # print(existing_varation_list)  # print the existing varation  list 

            if product_variation in existing_varation_list:
                # return HttpResponse('true')
                # increase the cart item quantity
                index = existing_varation_list.index(product_variation)  # in the exiting varation list of item of index is equal to the product_varation -> 2
                item_id = id[index]  # concatenate to the item id in the index -> 2
                item = CartItem.objects.get(product=product, id=item_id)  # fetch the Cartitem using product is equal to product and product id is equal to product id   -> 2
                item.quantity += 1 
                item.save()

            
            else:
                # return HttpResponse('False')
                # create a new cart item 
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)  # show the product of CartItem -> 2
                # -> 2 
                if len(product_variation) > 0:  # product varation is greter then 0 
                    item.variations.clear()  # first of all clear the variation and then add the variations 
                    item.variations.add(*product_variation)  # add the item in variation 
                item.save()

        else:
            
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user,
            )
            # -> 2
            if len(product_variation) > 0:  # product varation is greter then 0 
                cart_item.variations.clear()  # first of all clear the variation and then add the variations
                cart_item.variations.add(*product_variation)  # add the cart_item in variation 
            cart_item.save()
        # return HttpResponse(cart_item.product)
        # exit()

        return redirect('cart')


    else:
        # if user is not authenticated 
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                # print(key, value)
                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                    
                except:
                    pass




        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))

        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
            cart.save()

        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()  # check the product is exists or not
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)  # exists in the cart the filter the product = product 
            # existing varations -> database
            # current varation -> product varation 
            # item_id -> database
            existing_varation_list = [] # product is append in the list 
            id = []  # create the empty list id -> 2
            for item in cart_item:
                existing_varation = item.variations.all()   # all product varations are show 
                existing_varation_list.append(list(existing_varation))   # varations are append in the list of existing_varation_list 
                id.append(item.id) # append the item in id -> 2 

            print(existing_varation_list)  # print the existing varation  list 

            if product_variation in existing_varation_list:
                # return HttpResponse('true')
                # increase the cart item quantity
                index = existing_varation_list.index(product_variation)  # in the exiting varation list of item of index is equal to the product_varation -> 2
                item_id = id[index]  # concatenate to the item id in the index -> 2
                item = CartItem.objects.get(product=product, id=item_id)  # fetch the Cartitem using product is equal to product and product id is equal to product id   -> 2
                item.quantity += 1 
                item.save()

            
            else:
                # return HttpResponse('False')
                # create a new cart item 
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)  # show the product of CartItem -> 2
                # -> 2 
                if len(product_variation) > 0:  # product varation is greter then 0 
                    item.variations.clear()  # first of all clear the variation and then add the variations 
                    item.variations.add(*product_variation)  # add the item in variation 
                item.save()

        else:
            
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
            )
            # -> 2
            if len(product_variation) > 0:  # product varation is greter then 0 
                cart_item.variations.clear()  # first of all clear the variation and then add the variations
                cart_item.variations.add(*product_variation)  # add the cart_item in variation 
            cart_item.save()
        # return HttpResponse(cart_item.product)
        # exit()

        return redirect('cart')































































def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:

        # remove the authenticated user 
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)


        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)



        if cart_item.quantity > 1:
            cart_item.quantity -= 1 
            cart_item.save()

        else:
            cart_item.delete()
    except:
        pass

    return redirect('cart')

def remove_cart_item(request,product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)

    # remove for the authenticated user 
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)

    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

    cart_item.delete()
    return redirect('cart')




def cart(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)

        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (2 * total) / 100 
        grand_total = total + tax 

    except ObjectDoesNotExist:
        pass 

    context = {
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total,

    }

    return render(request, 'store/cart.html',context)



@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)

        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (2 * total) / 100 
        grand_total = total + tax 

    except ObjectDoesNotExist:
        pass 

    context = {
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total,

    }
    return render(request, 'store/checkout.html', context)
