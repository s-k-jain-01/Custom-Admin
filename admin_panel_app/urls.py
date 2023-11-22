from django.urls import path
from .views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('',adminindex,name='admin_index'),
    path('signin/',signin,name='signin'),
    path("logout_view/",logout_view,name="logout_view"),
    path('profile/',edit_profile,name='profile'),
    path('Change_Password/',Change_Password,name='Change_Password'),


    #user................................................
    path("userlist/",userlist,name="userlist"),
    path('adduser/',adduser,name='adduser'),
    path('profile_details/',profile_detail,name='profile_detail'),
    path('distributerlist/',distributerlist,name='distributerlist'),
    path('stafflist/',stafflist,name='stafflist'),
    path('delete_user/',delete_user,name='delete_user'),

    #blog................................................
    path('bloglist/',bloglist,name='bloglist'),
    path('addblog/',addblog,name='addblog'),
    path('updateblog/',updateblog,name='updateblog'), 
    path('deleteblog/',delete_blog,name='deleteblog'),

    #about...............................................
    path('about_us/',about_us,name='about_us'),
    path('update_about/',update_about,name='update_about'),

    #contact.............................................
    path('contact_us/',contact_us,name='contact_us'),
    path('reply_customer/',reply_customer,name='reply_customer'),

    #testimonial..........................................
    path('testimonials_list/',testimonials_list,name='testimonials_list'),
    path('addtest/',addtest,name='addtest'),
    path('updatetest/',updatetest,name='updatetest'),
    path('delete_test/',delete_test,name='delete_test'),

    #category..............................................
    path('cat_list/',cat_list,name='cat_list'),
    path('add_cat/',add_cat,name='add_cat'),
    path('update_cat/',update_cat,name='update_cat'),
    path('del_cat/',del_cat,name='del_cat'),

    #product...............................................
    path('product_list/',product_list,name='product_list'),
    path('add_product/',add_product,name='add_product'),
    path('update_product/',update_product,name='update_product'),
    path('del_product/',del_product,name='del_product'),

    #sub category...........................................
    path('sub_cat_list/',sub_cat_list,name='sub_cat_list'),
    path('add_sub_cat/',add_sub_cat,name='add_sub_cat'),
    path('update_sub_cat/',update_sub_cat,name='update_sub_cat'),
    path('del_sub_cat/',del_sub_cat,name='del_sub_cat'),

    # comapny.................................................
    path('company_list/',company_list,name='company_list'),
    path('add_company/',add_company,name='add_company'),
    path('update_company/',update_company,name='update_company'), 
    path('delete_company/',delete_company,name='delete_company'),

    #cart......................................................
    path('cart_list/',cart_list,name='cart_list'),
    path('update_cart/',update_cart,name='update_cart'),
    path('delete_cart/',delete_cart,name='delete_cart'),

    #address...................................................
    path('address_list/',address_list,name='address_list'),
    path('add_address/',add_address,name='add_address'),
    path('update_adres/',update_adres,name='update_adres'),
    path('delete_adres/',delete_adres,name='delete_adres'),

    #order......................................................
    path('orderlist/',orderlist,name='orderlist'),
    path('addorder/',addorder,name='addorder'),
    path('update_order/',update_order,name='update_order'),
    path('delete_order/',delete_order,name='delete_order'),
    path('invoice/',invoice,name='invoice'),
    path('send_invoice/',send_invoice,name='send_invoice'),
    
]+static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)