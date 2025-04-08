from django.shortcuts import render
from admin_management.models import Products,Category
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator





# Create your views here.

def productlists(request, pid):
    categories = Category.objects.all()

    if pid == 0:
        products = Products.objects.all()
        paginator = Paginator(products,4)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number) 

    else:
        print(pid)
        category = get_object_or_404(Category, id=pid)
        products = Products.objects.filter(category=category)
        paginator = Paginator(products,4)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number) 

        categories = Category.objects.all()


    return render(request, 'products/listproduct.html', locals())

def singleproductview(request,id):
        product= Products.objects.get(id=id)
        return render(request,'products/singleproductview.html',{'product':product})

def search(request):
    keyword = request.GET.get('keyword')
    products = Products.objects.filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword)).order_by('-created_date')
    paginator = Paginator(products, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'categories': Category.objects.all(),
        'products': products,
        'keyword' : keyword,
        'page_obj': page_obj
    }
    return render(request, 'products/listproduct.html', context)
