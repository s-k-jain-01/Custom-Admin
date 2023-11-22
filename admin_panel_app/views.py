from django.shortcuts import render,redirect,reverse
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from .models import *
from django.conf import settings
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.mail import EmailMessage
from pyhtml2pdf import converter
from django.core.exceptions import PermissionDenied
from datetime import timedelta
from django.utils import timezone
import razorpay
import os
media = settings.MEDIA_URL
client = razorpay.Client(auth=(settings.RAZORPAY_CLIENT_ID,settings.RAZORPAY_CLIENT_SECRET))

# Create your views here.
end_date = timezone.now() - timedelta(days=30)
start_date = end_date - timedelta(days=1)
Order.objects.filter(created_at__gte=start_date, created_at__lte=end_date).delete()
Cart.objects.filter(created_at__gte=start_date, created_at__lte=end_date, delete_status=1).delete()

def remove_image_from_media(image_path):
    os.remove(image_path)

def superuser_only(function):
    def _inner(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied  
            # raise Http404         
        return function(request, *args, **kwargs)
    return _inner

def staff_only(function):
    def _inner(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied  
            # raise Http404         
        return function(request, *args, **kwargs)
    return _inner

@login_required(login_url='signin')
def adminindex(request):
    today_money=0
    current_date = timezone.now().date()
    today_user=User.objects.filter(last_login__date=current_date).count()
    mny = Order.objects.filter(created_at__date=current_date)
    for i in mny:
        today_money=today_money+i.total_price
    print(today_user,today_money)
    return render(request,'admin/index1.html',{'today_user':today_user,'today_money':today_money})

def signin(request):
    if request.method == "POST":
        user=request.POST.get("username")
        passd=request.POST.get("password")
        user = authenticate(username=user,password=passd)
        if user :
            user = User.objects.get(id=user.id)
            login(request,user)  #to save login details in session table
            # request.session.set_expiry(1109600)
            if user.is_superuser or user.is_staff or user.user_type == 1:
                return redirect(adminindex)
            else:
                return render(request,"sign-in.html",{'output': 'User not found please enter correct details.'})
        else:
            return render(request,"sign-in.html",{'output': 'User not found please enter correct details.'})
    else:
        return render(request,"sign-in.html")


def logout_view(request):
    logout(request)
    return redirect('signin')

@login_required(login_url='signin')
def profile(request):
    return render(request,'profile.html')

# user.........

@login_required(login_url='signin')
def userlist(request):
    if request.user.is_staff or request.user.is_superuser:
        user=User.objects.filter(Q(user_type=0), Q(is_staff = False), Q(is_superuser=False)).order_by('-created_at')
    else:
        user=User.objects.filter(Q(user_type=0), Q(is_staff = False), Q(is_superuser=False),Q(postal_code = request.user.postal_code)).order_by('-created_at')
    paginator = Paginator(user,10)
    page_no = request.GET.get('page')
    user_obj = paginator.get_page(page_no)
    return render(request,'users/userlist.html',{'user_obj':user_obj})

@login_required(login_url='signin')
@staff_only
def distributerlist(request):
    user=User.objects.filter(Q(user_type=1) , Q(is_staff = False), Q(is_superuser=False)).order_by('-created_at').exclude(username=request.user)
    paginator = Paginator(user,10)
    page_no = request.GET.get('page')
    user_obj = paginator.get_page(page_no)
    return render(request,'users/userlist.html',{'user_obj':user_obj})

@login_required(login_url='signin')
@superuser_only
def stafflist(request):
    user = User.objects.filter(Q(is_staff = True), Q(is_superuser=False)).order_by('-created_at').exclude(username=request.user)
    paginator = Paginator(user,10)
    page_no = request.GET.get('page')
    user_obj = paginator.get_page(page_no)
    return render(request,'users/userlist.html',{'user_obj':user_obj})

#Profile.........

@login_required(login_url='signin')
def profile_detail(request):
    if request.method == 'GET':
        user_id=request.GET.get('user_id')
        user=User.objects.filter(id=user_id)
        return render(request,'user_profile/profile_detail.html',{'user':user})
    else:
        user_id=request.POST.get('user_id')
        user = User.objects.get(id=user_id)
        user.delete_status=request.POST.get('block')
        user.save()
        if user.is_staff == False:
            return redirect('userlist')
        else:
            return redirect('distributerlist')
        
@login_required(login_url='signin')
def adduser(request):
    if request.method == "POST":
        user_type = int(request.POST.get('user_type'))
        user=User()
        user.username=request.POST.get("username")
        password=request.POST.get("password")
        user.email = request.POST.get('email')
        user.first_name=request.POST.get('fname')
        user.last_name=request.POST.get('lname')
        user.mobile_no=request.POST.get('mobile_no')
        if user_type == 2:
            user.is_staff=True
        else:
            user.user_type=user_type
        user.address=request.POST.get('address')
        user.city=request.POST.get('city')
        user.postal_code=request.POST.get('postal_code')
        user.set_password(password)
        user.save()
        if user_type == 0:
            return redirect('userlist')
        elif user_type == 2:
            return redirect('stafflist')
        else:
            return redirect('distributerlist')
    return render(request,"users/adduser.html")


@login_required(login_url='signin')
def edit_profile(request):
    if request.method == "GET":
        user=User.objects.filter(id=request.user.id)
        return render(request,'users/profile.html',{'user':user})
    else:
        user=User.objects.get(id=request.user.id)
        user.first_name=request.POST.get('first_name')
        user.last_name=request.POST.get('last_name')
        user.postal_code=request.POST.get('postal_code')
        user.city=request.POST.get('city')
        user.address=request.POST.get('address')
        user.mobile_no=request.POST.get('mobile_no')
        user.save()
        return redirect('profile')

@login_required(login_url='signin')
@staff_only
def delete_user(request):
    user_id = request.GET.get('user_id')
    user = User.objects.get(id=user_id)
    user.delete()
    if user.is_staff == False:
        return redirect('userlist')
    else:
        return redirect('distributerlist')

@login_required(login_url='signin')
def Change_Password(request):
    msg=""
    if request.method == "POST":
        oldpassword = request.POST.get('oldpassword')
        newpassword1 = request.POST.get('newpassword1')
        newpassword2 = request.POST.get('newpassword2')
        if newpassword1 == newpassword2 :
            user = authenticate(username=request.user, password=oldpassword)
            if user is not None:
                u = User.objects.get(username=request.user)
                u.set_password(newpassword2)
                u.save()
                return redirect('signin')
        else:
            msg="please enter correct password"
    return render(request,"users/change_password.html",{'msg':msg})

#blog........................................

@login_required(login_url='signin')
@staff_only
def bloglist(request):
    blog = Blog.objects.all()
    paginator = Paginator(blog,10)
    page_no = request.GET.get('page')
    blog_obj = paginator.get_page(page_no)
    return render(request,'blogs/bloglist.html',{'blog_obj':blog_obj})

@login_required(login_url='signin')
@staff_only
def addblog(request):
    if request.method == "POST":
        blog=Blog()
        blog.blog_topic=request.POST.get("topic")
        blog.blog_title=request.POST.get("title")
        blog.blog_img = request.FILES.get('img')
        blog.blog_desc =request.POST.get('desc')
        blog.save()
        return redirect('bloglist')
    return render(request,'blogs/addblog.html')

@login_required(login_url='signin')
@staff_only
def updateblog(request):
    if request.method == "GET":
        blog_id=request.GET.get('blog_id')
        blog=Blog.objects.filter(id=blog_id)
        media1=media
        return render(request,"blogs/updateblog.html",{'blog':blog,'media':media1})
    else:
        blog_id=request.POST.get('blog_id')
        blog=Blog.objects.get(id=blog_id)
        blog.blog_topic=request.POST.get("topic")
        blog.blog_title=request.POST.get("title")
        img = request.FILES.get('img')
        blog.blog_desc =request.POST.get('desc')
        blog.delete_status = request.POST.get('status')
        if img:
            blog.blog_img=img
            blog1=Blog.objects.get(id=blog_id)
            blog_image_path = blog1.blog_img.path
            remove_image_from_media(blog_image_path)
        blog.save()
        return redirect('bloglist')

@login_required(login_url='signin')
@staff_only
def delete_blog(request):
    blog_id=request.GET.get('blog_id')
    Blog.objects.filter(id=blog_id).delete()
    return redirect('bloglist')

#About................................................

@login_required(login_url='signin')
@staff_only
def about_us(request):
    about_us = AboutUs.objects.all()
    return render(request,'about_us/about_us.html',{'about_us':about_us})

@login_required(login_url='signin')
@staff_only
def update_about(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        about = AboutUs.objects.filter(id=id)
        media1 = media
        return render(request,'about_us/update_about.html',{'about':about,'media':media1})
    else:
        about_id = request.POST.get('about_id')
        about = AboutUs.objects.get(id=about_id)
        about.about_title = request.POST.get('title')
        about.about_desc = request.POST.get('desc')
        about.delete_status = request.POST.get('status')
        img = request.FILES.get('img')
        if img:
            about.about_img = img
            about1=AboutUs.objects.get(id=about_id)
            about_image_path = about1.about_img.path
            remove_image_from_media(about_image_path)
        about.save()
        return redirect('about_us')


#testimonials...........................................

@login_required(login_url='signin')
@staff_only
def testimonials_list(request):
    test = Testimonials.objects.all()
    paginator = Paginator(test,10)
    test_obj = paginator.get_page(request.GET.get('page'))
    return render(request,'testimonials/testimonials_list.html',{'test_obj':test_obj})

@login_required(login_url='signin')
@staff_only
def addtest(request):
    if request.method == 'POST':
        test = Testimonials()
        test.test_title = request.POST.get('title')
        test.test_img = request.FILES.get('img')
        test.test_desc = request.POST.get('desc')
        test.save()
        return redirect('testimonials_list')
    return render(request,'testimonials/addtest.html')

@login_required(login_url='signin')
@staff_only
def updatetest(request):
    if request.method == "GET":
        test_id=request.GET.get('test_id')
        test=Testimonials.objects.filter(id=test_id)
        media1=media
        return render(request,'testimonials/updatetest.html',{'test':test,'media':media1})
    
    else:
        test_id=request.POST.get('test_id')
        test=Testimonials.objects.get(id=test_id)
        test.test_title=request.POST.get("title")
        img = request.FILES.get('img')
        test.test_desc =request.POST.get('desc')
        test.delete_status = request.POST.get('status')
        if img:
            test.test_img=img
            test1=Testimonials.objects.get(id=test_id)
            test_image_path = test1.test_img.path
            remove_image_from_media(test_image_path)
        test.save()
        return redirect('testimonials_list')

@login_required(login_url='signin')
@staff_only
def delete_test(request):
    test_id=request.GET.get('test_id')
    Testimonials.objects.filter(id=test_id).delete()
    return redirect('testimonials_list')

#product............................................

@login_required(login_url='signin')
def product_list(request):
    product = Product.objects.all()
    paginator = Paginator(product,10)
    page_no = request.GET.get('page')
    pro_obj = paginator.get_page(page_no)
    return render(request,'product/product_list.html',{'pro_obj':pro_obj})

def add_product(request):
    if request.method == 'GET':
        sub_cat = Sub_Category.objects.all()
        company = Company.objects.all()
        return render(request,'product/add_product.html',{'sub_cat':sub_cat,'company':company})
    else:
        
        product = Product()
        product.sub_cat =  Sub_Category.objects.get(id = request.POST.get('sub_cat'))
        product.company_name = Company.objects.get(id = request.POST.get('company'))
        product.pro_name = request.POST.get('name')
        product.pro_img = request.FILES.get('img')
        product.pro_price = request.POST.get('price')
        product.pro_desc = request.POST.get('desc')
        product.stock = request.POST.get('stock')
        product.varient = request.POST.get('varient')
        product.discount_price = request.POST.get('discount_price')
        product.qty_type = request.POST.get('qty_type')
        product.quantity = request.POST.get('quantity')
        product.save()
        quantity=request.POST.getlist('quantity[]')
        q_price=request.POST.getlist('q_price[]')
        multiple_img=request.FILES.getlist('prduct_img[]')
        for i in range(len(quantity)):
            Volume.objects.create(product_id=product.id,quanity=quantity[i],price = q_price[i])
        for j in range(len(multiple_img)):
            Product_img.objects.create(product_id=product.id,image=multiple_img[j])
        return redirect('product_list')
    
@login_required(login_url='signin')
def update_product(request):
    if request.method == 'GET':
        pro_id = request.GET.get('pro_id')
        product = Product.objects.filter(id=pro_id)
        sub_cat = Sub_Category.objects.all()
        company = Company.objects.all()
        media1 = media
        return render(request,'product/update_product.html',{'product':product,'sub_cat':sub_cat,'media':media1,'company':company})
    else:
        pro_id = request.POST.get('pro_id')
        product = Product.objects.get(id = pro_id)
        product.sub_cat =  Sub_Category.objects.get(id = request.POST.get('sub_cat'))
        product.company_name = Company.objects.get(id = request.POST.get('company'))
        product.pro_name = request.POST.get('name')
        product.pro_price = request.POST.get('price')
        product.pro_desc = request.POST.get('desc')
        product.stock = request.POST.get('stock')
        product.varient = request.POST.get('varient')
        product.discount_price = request.POST.get('discount_price')
        product.qty_type = request.POST.get('qty_type')
        product.quantity = request.POST.get('quantity')
        product.delete_status = request.POST.get('status')
        img = request.FILES.get('img')
        if img:
            product.pro_img=img
            product1=Product.objects.get(id=pro_id)
            product_image_path = product1.pro_img.path
            remove_image_from_media(product_image_path)
        product.save()
        return redirect('product_list')

@login_required(login_url='signin')
def del_product(request):
    pro_id = request.GET.get('pro_id')
    Product.objects.filter(id=pro_id).delete()
    return redirect('product_list')

#category.........................................

@login_required(login_url='signin')
@staff_only
def cat_list(request):
    cat_list = Category.objects.all()
    paginator = Paginator(cat_list,10)
    page_no = request.GET.get('page')
    cat_obj = paginator.get_page(page_no)
    return render(request,'category/cat_list.html',{'cat_obj':cat_obj})

@login_required(login_url='signin')
@staff_only
def add_cat(request):
    if request.method == 'POST':
        cat = Category()
        cat.cat_name = request.POST.get('name')
        cat.cat_img = request.FILES.get('img')
        cat.cat_desc = request.POST.get('desc')
        cat.save()
        return redirect('cat_list')
    else:
        return render(request,'category/add_cat.html')

@login_required(login_url='signin')
@staff_only
def update_cat(request):
    if request.method == 'GET':
        cat_id = request.GET.get('cat_id')
        cat = Category.objects.filter(id=cat_id)
        media1 = media
        return render(request,'category/update_cat.html',{'cat':cat,'media':media1})
    else:
        cat_id = request.POST.get('cat_id')
        cat = Category.objects.get(id=cat_id)
        cat.cat_name=request.POST.get('name')
        cat.cat_desc=request.POST.get('desc')
        cat.delete_status=request.POST.get('status')
        img=request.FILES.get('img')
        if img:
            cat.cat_img=img
            cat1=Category.objects.get(id=cat_id)
            seed_img_path=cat1.cat_img.path
            remove_image_from_media(seed_img_path)
        cat.save()
        return redirect('cat_list')

@login_required(login_url='signin')
@staff_only
def del_cat(request):
    cat_id = request.GET.get('cat_id')
    Category.objects.filter(id=cat_id).delete()
    return redirect('cat_list')

#sub category.........................................

@login_required(login_url='signin')
@staff_only
def sub_cat_list(request):
    sub_cat = Sub_Category.objects.all()
    paginator = Paginator(sub_cat,10)
    page_no = request.GET.get('page')
    sub_obj = paginator.get_page(page_no)
    return render(request,'sub_cat/sub_cat_list.html',{'sub_obj':sub_obj})

@login_required(login_url='signin')
@staff_only
def add_sub_cat(request):
    if request.method == 'POST':
        sub_cat = Sub_Category()
        sub_cat.category =  Category.objects.get(id = request.POST.get('category'))
        sub_cat.sub_cat_name = request.POST.get('name')
        sub_cat.sub_cat_img = request.FILES.get('img')
        sub_cat.sub_cat_desc = request.POST.get('desc')
        
        sub_cat.save()
        return redirect('sub_cat_list')
    else:
        category = Category.objects.all()
        return render(request,'sub_cat/add_sub_cat.html',{'category':category})

@login_required(login_url='signin')  
@staff_only 
def update_sub_cat(request):
    if request.method == 'GET':
        sub_cat_id = request.GET.get('sub_cat_id')
        category = Category.objects.all()
        sub_cat = Sub_Category.objects.filter(id=sub_cat_id)
        media1 = media
        return render(request,'sub_cat/update_sub_cat.html',{'sub_cat':sub_cat,'media':media1,'category':category})
    else:
        sub_cat_id = request.POST.get('sub_cat_id')
        sub_cat = Sub_Category.objects.get(id=sub_cat_id)
        sub_cat.category =  Category.objects.get(id = request.POST.get('category'))
        sub_cat.sub_cat_name=request.POST.get('name')
        sub_cat.sub_cat_desc=request.POST.get('desc')
        sub_cat.delete_status=request.POST.get('status')
        img=request.FILES.get('img')
        if img:
            sub_cat.sub_cat_img=img
            sub_cat1=Sub_Category.objects.get(id=sub_cat_id)
            variety_img_path=sub_cat1.sub_cat_img.path
            remove_image_from_media(variety_img_path)
        sub_cat.save()
        return redirect('sub_cat_list')

@login_required(login_url='signin')    
@staff_only
def del_sub_cat(request):
    sub_cat_id = request.GET.get('sub_cat_id')
    Sub_Category.objects.filter(id=sub_cat_id).delete()
    return redirect('sub_cat_list')

#contact................................................ 

@login_required(login_url='signin')
@staff_only
def contact_us(request):
    contact_us = Contact_Us.objects.all().order_by("-updated_at")
    paginator = Paginator(contact_us,10)
    page_no = request.GET.get('page')
    contact_obj = paginator.get_page(page_no)
    return render(request,'contact_us/contact_us.html',{'contact_obj':contact_obj})

@login_required(login_url='signin')
@staff_only
def reply_customer(request):
    if request.method == 'GET':
        contact_id = request.GET.get('contact_id')
        contact = Contact_Us.objects.filter(id=contact_id)
        return render(request,'contact_us/reply_customer.html',{'contact':contact})
    else:
        contact_id = request.POST.get('contact_id')
        reply_msg = request.POST.get('message')
        contact = Contact_Us.objects.get(id=contact_id)
        send_mail(
            request.POST.get('subject'),
            reply_msg,
            settings.EMAIL_HOST_USER,
            [request.POST.get('mail')]
        )
        contact.reply_msg = reply_msg
        contact.save()
        return redirect('contact_us')
    
# company.................................................

@login_required(login_url='signin')
def company_list(request):
    cmpny = Company.objects.all()
    paginator = Paginator(cmpny,10)
    cmpny_obj = paginator.get_page(request.GET.get('page'))
    return render(request,'company/companylist.html',{'cmpny_obj':cmpny_obj})


@login_required(login_url='signin')
def add_company(request):
    product=Product.objects.all()
    if request.method == "POST":
        cmpny=Company()
        cmpny.company_name=request.POST.get("company_name")
        cmpny.save()
        return redirect('company_list')
    
    return render(request,'company/addcompany.html',{'product':product})

@login_required(login_url='signin')
def update_company(request):
    if request.method == "GET":
        cmpny_id=request.GET.get('cmpny_id')
        cmpny=Company.objects.filter(id=cmpny_id)
        media1=media
        return render(request,"company/updatecompany.html",{'cmpny':cmpny,'media':media1})
    else:
        cmpny_id=request.POST.get('cmpny_id')
        cmpny=Company.objects.get(id=cmpny_id)
        cmpny.company_name=request.POST.get("company_name")
        cmpny.delete_status = request.POST.get('status')
        cmpny.save()
        return redirect('company_list')

@login_required(login_url='signin')
def delete_company(request):
    cmpny_id=request.GET.get('cmpny_id')
    Company.objects.filter(id=cmpny_id).delete()
    return redirect('company_list')

#cart...................................................

@login_required(login_url='signin')
def cart_list(request):
    user_id = request.GET.get('user_id')
    cart = Cart.objects.filter(customer = user_id, delete_status = 0).order_by('-updated_at')
    paginator = Paginator(cart,10)
    page_no = request.GET.get('page')
    cart_obj = paginator.get_page(page_no)
    return render(request,'cart/cart_list.html',{'cart_obj':cart_obj})

@login_required(login_url='signin')
def update_cart(request):
    if request.method == 'GET':
        cart_id = request.GET.get('cart_id')
        cart = Cart.objects.filter(id=cart_id)
        return render(request,'cart/update_cart.html',{'cart':cart})
    else:
        cart_id = request.POST.get('cart_id')
        cart = Cart.objects.get(id=cart_id)
        cart.quantity=request.POST.get('qty')
        cart.save()
        return redirect(reverse('cart_list')+'?user_id='+str(cart.customer.id))
    
@login_required(login_url='signin')    
def delete_cart(request):
    user_id = request.GET.get('user_id')
    cart_id = request.GET.get('cart_id')
    Cart.objects.filter(id=cart_id).delete()
    return redirect(reverse('cart_list')+'?user_id='+user_id)

#address..................................................
@login_required(login_url='signin')
def address_list(request):
    user_id = request.GET.get('user_id')
    address = Address.objects.filter(custuser=user_id)
    paginator = Paginator(address,10)
    page_no = request.GET.get('page')
    adres_obj = paginator.get_page(page_no)
    return render(request,'address/adres_list.html',{'adres_obj':adres_obj,'user_id':user_id})

@login_required(login_url='signin')
def add_address(request):
    if request.method == 'POST':
        user_id = request.POST.get('user')
        adres = Address()
        adres.custuser = User.objects.get(id=user_id)
        adres.name = request.POST.get('name')
        adres.mobile = request.POST.get('mobile_no')
        adres.pin = request.POST.get('pin')
        adres.adres = request.POST.get('address')
        adres.locality = request.POST.get('locality')
        adres.city = request.POST.get('city')
        adres.state = request.POST.get('state')
        adres.save()
        return redirect(reverse('address_list')+'?user_id='+user_id)
    else:
        user = User.objects.filter(id=request.GET.get('user_id')).first()
        return render(request,'address/add_adres.html',{'user':user})
    
@login_required(login_url='signin')
def update_adres(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        adres = Address.objects.get(id=request.POST.get('adres_id'))
        adres.name = request.POST.get('name')
        adres.mobile = request.POST.get('mobile_no')
        adres.pin = request.POST.get('pin')
        adres.adres = request.POST.get('address')
        adres.locality = request.POST.get('locality')
        adres.city = request.POST.get('city')
        adres.state = request.POST.get('state')
        adres.save()
        return redirect(reverse('address_list')+'?user_id='+user_id)
    else:
        adres = Address.objects.filter(id=request.GET.get('adres_id'))
        return render(request,'address/update_adres.html',{'adres':adres})
    
@login_required(login_url='signin')
def delete_adres(request):
    user_id = request.GET.get('user_id')
    Address.objects.filter(id=request.GET.get('adres_id')).delete()
    return redirect(reverse('address_list')+'?user_id='+user_id)
    
#order..............................................................

@login_required(login_url='signin')
def orderlist(request):
    user_id = request.GET.get('user_id')
    if user_id:
        cart = Cart.objects.filter(customer = user_id)
        order = Order.objects.filter(cart__in = cart).order_by('-updated_at')
        paginator = Paginator(order,10)
        order_obj = paginator.get_page(request.GET.get('page'))
        return render(request,'order/orderlist.html',{'order_obj':order_obj,'user_id':user_id})

    order = Order.objects.all().order_by('-updated_at')
    paginator = Paginator(order,10)
    order_obj = paginator.get_page(request.GET.get('page'))
    return render(request,'order/orderlist.html',{'order_obj':order_obj})

def addorder(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        amount = float(request.POST.get('total_price'))
        tax = float(request.POST.get('tax'))
        amount += tax
        res = client.order.create({
            'amount':amount*100,
            'currency':'INR'
        })
        cart_ids=request.POST.getlist('cart')
        for cart in cart_ids:
            order = Order()
            order.cart = Cart.objects.get(id=cart)
            order.address = Address.objects.get(id=request.POST.get('address'))
            order.order_id = res['id']
            order.total_price = amount
            order.save()
        return redirect(reverse('orderlist')+'?user_id='+user_id)
    else:
        total_price = 0
        user = User.objects.get(id=request.GET.get('user_id'))
        cart = Cart.objects.filter(customer = user, delete_status=0)
        address = Address.objects.filter(custuser = user)
        for amount in cart:
            total_price += amount.quantity * int(amount.product.pro_price)
        return render(request,'order/addorder.html',{'cart':cart,'address':address,'total_price':total_price,'user_id':user.id})

def update_order(request):
    order_id = request.GET.get('order_id')
    user_id = request.GET.get('user_id')
    order = Order.objects.get(id=order_id)
    order.booking_status = request.GET.get('booking_status')
    order.save()
    return redirect(reverse('orderlist')+'?user_id='+user_id)

def delete_order(request):
    user_id = request.GET.get('user_id')
    Order.objects.filter(id=request.GET.get('order_id')).delete()
    return redirect(reverse('orderlist')+'?user_id='+user_id)

def invoice(request):
    sub_total=0
    order = Order.objects.filter(order_id=request.GET.get('order_id'))
    for i in order:
        sub_total += int(i.cart.product.pro_price)*int(i.cart.quantity)
    return render(request,'invoice/invoice.html',{'order':order,'sub_total':sub_total})

def send_invoice(request):
    order_id=request.GET.get('order_id')
    user_id = request.GET.get('user_id')
    converter.convert('http://127.0.0.1:8000/admin/invoice/?order_id='+order_id, 'invoice.pdf')
    get_order=Order.objects.filter(order_id=order_id).first()
    mail_to = get_order.cart.customer.email

    email = EmailMessage(
        'Invoice from Kisansewa', 'Here is the message.', settings.EMAIL_HOST_USER, [mail_to])
    email.attach_file('invoice.pdf')
    email.send()
    return redirect(reverse('orderlist')+'?user_id='+user_id)