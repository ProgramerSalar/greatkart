from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account,Userprofile
# Create your views here.


# verification the email 
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode , urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages , auth
from django.contrib.auth.decorators import login_required


from carts.models import Cart,CartItem
from carts.views import _cart_id


from orders.models import Order, OrderProduct


import requests

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username=email.split("@")[0]

            user = Account.objects.create_user(first_name=first_name,
                                               last_name=last_name,
                                               email=email,
                                               username=username,
                                               password=password)
            user.phone_number = phone_number
            user.save()
            # messages.success(request, 'Registration Succesful')
            # return redirect('register')

            # user activation 
            current_site = get_current_site(request)
            mail_subject="Please activate you account"
            message = render_to_string('accounts/account_verification_email.html', {
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),

            })
            to_email = email
            send_email = EmailMessage(mail_subject,
                                      message, 
                                      to=[to_email])
            send_email.send()
            # messages.success(request, 'Thank you for registering with us. we have sent you a verification email to your email address. Please verify it.')
            return redirect('/accounts/login/?command=verification&email='+email)

        
    else:
        form = RegistrationForm()


    context = {
        'form':form,
    }

    return render(request, 'accounts/register.html',context)




def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))  # cart id are store in cart variable 
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()  # check the product is exists or not
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    # getting the product variation by cart id 
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    # get the cart items form the user access his product variation 
                    cart_item = CartItem.objects.filter(user=user)
                    existing_varation_list = [] # product is append in the list 
                    id = []  # create the empty list id -> 2
                    for item in cart_item:
                        existing_varation = item.variations.all()   # all product varations are show 
                        existing_varation_list.append(list(existing_varation))   # varations are append in the list of existing_varation_list 
                        id.append(item.id) # append the item in id -> 2 


                    # product_variation = [1,3,5,4]
                    # existing_varation_list = [3, 4, 5, 6, 7]  # when any item are commin list 1 , this comman items are added 
                    for pr in product_variation:
                        if pr in existing_varation_list:
                            index = existing_varation_list.index(pr)  # comman item in product_variation and existing_variation_list 
                            item_id = id[index]  # comman item id is store in item_id 
                            item = CartItem.objects.get(id=item_id)  # push the common item in cartitem 
                            item.quantity += 1  # add the common item 
                            item.user = user   # item is assign the  user 
                            item.save()  

                        else:
                            # when item is not common, add item in the cart 
                            cart_item = CartItem.objects.filter(cart=cart)  # filter the item in the cart 
                            for item in cart_item:  
                                item.user = user    # assign the user 
                                item.save()






                    

            except:
                pass
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')


            # redirect the page of depend on user which is check 
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query   # which point you clicked to login for example of when you have checkout page and then checkout click and go to login page (this code is show the next=/cart/checkout/ ) this things
                # print('query -> ', query)
                # next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))  # and then you have next=/cart/checkout/ this things (you are split to in the dictionary next is the key and /cart/checkout/ is value)
                # print('params -> ', params)
                if 'next' in params:
                    nextPage = params['next']  # when you are logged in you go the next page,  and next is /cart/checkout/ this url 
                    return redirect(nextPage)  # you go to the next page url 
                
            except:
                return redirect('dashboard')
                
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')



@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')
    return HttpResponse('logout')




def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)

    except(TypeError,ValueError,OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'congratulations! Your account is activated.')
        return redirect('login')

    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')


  
@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()
    context = {
        'orders_count':orders_count,
    }
    return render(request, 'accounts/dashboard.html',context)




def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            # user activation 
            current_site = get_current_site(request)
            mail_subject="Reset your password"
            message = render_to_string('accounts/reset_password_email.html', {
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),

            })
            to_email = email
            send_email = EmailMessage(mail_subject,
                                      message, 
                                      to=[to_email])
            send_email.send()
            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')

        else:
            messages.error(request, 'Account does not exists')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')




def resetPassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)

    except(TypeError,ValueError,OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid 
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')

    
  
def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset Successful')
            return redirect('login')

        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
        
    else:
        return render(request, 'accounts/resetPassword.html')
    



def my_orders(request):
    orders = Order.objects.filter(user=request.user,is_ordered=True).order_by('-created_at')   # filter the order in increasing oder ('-' means, '-created_at')
    context = {
        'orders':orders
    }
    return render(request, 'accounts/my_orders.html',context)






def edit_profile(request):
    userprofile = get_object_or_404(Userprofile, user=request.user)
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your Prfile has been updated')
            return redirect('edit_profile')
        

    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)


    context = {
        'user_form':user_form,
        'profile_form':profile_form,
        'userprofile':userprofile,
    }
    return render(request, 'accounts/edit_profile.html',context)



































