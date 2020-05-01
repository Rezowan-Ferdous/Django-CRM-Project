from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Customer(models.Model):
    user=models.OneToOneField(User,null=True,blank=True,on_delete=models.CASCADE)#when user deleted relationship delete
    name=models.CharField(max_length=200)
    phone=models.CharField(max_length=200)
    profile_pic=models.ImageField(default="rezowan.jpg",null=True,blank=True)
    email=models.CharField(max_length=200,null=True)
    date_created=models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name=models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Product(models.Model):
    CATEGORY=(('in door','in door'),
            ('out door','out door'),)
    name=models.CharField(max_length=200)
    price=models.FloatField(null=True)
    category=models.CharField(max_length=200,null=True ,choices=CATEGORY)
    description=models.CharField(max_length=500)
    date_created=models.DateTimeField(auto_now_add=True,null=True)
    tags = models.ManyToManyField(Tag)
    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS=(('pending','pending'),
    ('out of delivery','out of delivery'),
    ('delivered','delivered'),)
    customer = models.ForeignKey(Customer,null=True,on_delete=models.SET_NULL)
    product = models.ForeignKey(Product,null=True,on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True,null=True)
    status = models.CharField(max_length=200, choices=STATUS)
    note=models.CharField(max_length=1200,null=True)
    def __str__(self):
        return self.product.name
