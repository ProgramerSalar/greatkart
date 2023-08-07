from django.shortcuts import render, redirect
from django.shortcuts import HttpResponse, get_object_or_404
from .models import Product
from category.models import Category
from carts.models import Cart,CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q 

from .models import ReviewRating
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct





# Create your views here.
def store(request,category_slug=None):
    categories = None 
    product = None 
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        product_count = products.count()
        paginator = Paginator(products,3)  # one page have 6 products
        page = request.GET.get('page')   # in the url ,when you are go to the next page , the url is change that is page-2,page-3 like this 
        paged_products = paginator.get_page(page) 

    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        product_count = products.count()
        paginator = Paginator(products,3)  # one page have 6 products
        page = request.GET.get('page')   # in the url ,when you are go to the next page , the url is change that is page-2,page-3 like this 
        paged_products = paginator.get_page(page)   # page and paginator are conclude to one veriable that is paged_products 




    context = {
        'products':paged_products,
        'product_count':product_count,

    }
    return render(request, 'store/store.html',context)



def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request),product=single_product).exists()
        # return HttpResponse(in_cart)
        # exit()
    except Exception as e:
        raise e
    
    try:
        orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()

    except OrderProduct.DoesNotExist:
        orderproduct = None



    # get the reviews 
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
    
    context = {
        'single_product':single_product,
        'in_cart':in_cart,
        'orderproduct':orderproduct,
        'reviews':reviews,
    }

    return render(request, 'store/product_detail.html',context)







def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))   # search on descriptions 
            product_count = products.count()


    context = {
        'products':products,
        'product_count':product_count,
    }


    return render(request, 'store/store.html', context)







def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == "POST":
        try:
            # check review 
            reivews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reivews)   # instance means update the review 
            form.save()
            messages.success(request, 'Thank you! Your review is updated')
            return redirect(url)
        

        except ReviewRating.DoesNotExist:
            # create the review 
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id 
                data.save()

                messages.success(request, 'Thank you! Your review is updated')
                return redirect(url)





