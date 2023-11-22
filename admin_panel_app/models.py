from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from ckeditor.fields import RichTextField


class User(AbstractUser):
    mobile_no = models.CharField(max_length=50, blank=True, null=True, default="")
    user_type = models.IntegerField(blank=True, null=True, default=0)
    city = models.CharField(max_length=50, blank=True, null=True, default="")
    address = models.TextField(blank=True, null=True, default="")
    postal_code = models.CharField(max_length=50, blank=True, null=True, default="")
    front_id = models.CharField(max_length=50, blank=True, null=True, default="")
    profile = models.FileField(
        upload_to="profile_image", blank=True, null=True, default=""
    )
    delete_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class Address(models.Model):
    custuser = models.ForeignKey(
        User,
        related_name="custuser",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default="",
    )
    name = models.CharField(max_length=150, blank=True, null=True, default="")
    mobile = models.CharField(max_length=50, blank=True, null=True, default="")
    pin = models.CharField(max_length=150, blank=True, null=True, default="")
    adres = models.TextField(blank=True, null=True, default="")
    locality = models.CharField(max_length=150, blank=True, null=True, default="")
    city = models.CharField(max_length=150, blank=True, null=True, default="")
    state = models.CharField(max_length=150, blank=True, null=True, default="")

    def __str__(self) -> str:
        return self.adres


class Blog(models.Model):
    blog_title = models.CharField(max_length=500, blank=True, null=True, default="")
    blog_img = models.FileField(
        upload_to="blog_image", blank=True, null=True, default=""
    )
    blog_desc = RichTextField(blank=True, null=True)
    blog_topic = models.CharField(max_length=500, blank=True, null=True, default="")
    delete_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.blog_title


class Category(models.Model):  # dalhal, tilhan
    cat_name = models.CharField(max_length=50, blank=True, null=True, default="")
    cat_img = models.FileField(
        upload_to="category_image", blank=True, null=True, default=""
    )
    cat_desc = RichTextField(blank=True, null=True, default="")
    delete_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.cat_name


class Sub_Category(models.Model):
    category = models.ForeignKey(
        Category,
        related_name="category",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    sub_cat_name = models.CharField(max_length=100, null=True, blank=True)
    sub_cat_img = models.ImageField(upload_to="sub_category", null=True, blank=True)
    sub_cat_desc = RichTextField(null=True, blank=True, default="")
    delete_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.sub_cat_name


class Company(models.Model):
    company_name = models.CharField(max_length=100, blank=True, null=True)
    delete_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name


class Product(models.Model):
    sub_cat = models.ForeignKey(
        Sub_Category,
        related_name="sub_cat",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    comapny_name = models.ForeignKey(
        Company,
        related_name="comapny_name",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    pro_name = models.CharField(max_length=50, null=True, blank=True)
    pro_img = models.ImageField(upload_to="product", null=True, blank=True)
    pro_desc = RichTextField(null=True, blank=True, default="")
    pro_price = models.CharField(max_length=50, null=True, blank=True)
    stock = models.IntegerField(default=0)
    varient = models.IntegerField(default=0)  # 1 for liquid 2 for powder
    discount_price = models.CharField(max_length=50, null=True, blank=True)
    qty_type = models.CharField(max_length=50, null=True, blank=True)
    quantity = models.CharField(max_length=50, null=True, blank=True)
    delete_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.pro_name


class Product_img(models.Model):
    image = models.ImageField(upload_to="product/product_img", null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class Volume(models.Model):
    product = models.ForeignKey(
        Product, related_name="volume", on_delete=models.CASCADE, null=True, blank=True
    )
    quanity = models.FloatField(default=0, blank=True, null=True)
    price = models.FloatField(default=0, blank=True, null=True)
    delete_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.pro_name


class Cart(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="cart_product",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    customer = models.ForeignKey(
        User, related_name="customer", on_delete=models.CASCADE, blank=True, null=True
    )
    quantity = models.FloatField(default=0, blank=True, null=True)
    delete_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.product.pro_name


class Order(models.Model):
    cart = models.ForeignKey(
        Cart, related_name="cart", on_delete=models.CASCADE, null=True, blank=True
    )
    address = models.ForeignKey(
        Address, related_name="address", on_delete=models.CASCADE, null=True, blank=True
    )
    order_id = models.CharField(max_length=50, null=True, default=0)
    payment_id = models.CharField(max_length=50, null=True, default=0)
    booking_status = models.IntegerField(blank=True, null=True, default=0)
    total_price = models.IntegerField(blank=True, null=True, default=0)
    delete_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


class Testimonials(models.Model):
    test_title = models.CharField(max_length=500, blank=True, null=True, default="")
    test_img = models.FileField(
        upload_to="test_image", blank=True, null=True, default=""
    )
    test_desc = RichTextField(blank=True, null=True, default="")
    delete_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.test_title


class Contact_Us(models.Model):
    first_name = models.CharField(max_length=100, blank=True, null=True, default="")
    last_name = models.CharField(max_length=100, blank=True, null=True, default="")
    email = models.EmailField(max_length=254, blank=True, null=True, default="")
    mobile_no = models.CharField(max_length=100, blank=True, null=True, default="")
    reply_msg = models.CharField(max_length=100, blank=True, null=True, default="")
    msg = models.TextField(blank=True, null=True, default="")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name


class AboutUs(models.Model):
    about_title = models.CharField(max_length=500, blank=True, null=True, default="")
    about_img = models.FileField(
        upload_to="about_image", blank=True, null=True, default=""
    )
    about_desc = RichTextField(blank=True, null=True, default="")
    delete_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.about_title