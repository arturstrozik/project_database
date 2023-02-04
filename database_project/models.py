from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.validators import MinValueValidator


class Products(models.Model):
    # product id
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    quantity_in_stock = models.FloatField(validators=[MinValueValidator(0.0)], default=0.0)
    unit = models.CharField(max_length=5)
    serial_number = models.DateTimeField()
    expiration_date_in_days = models.PositiveIntegerField()
    price = models.FloatField(validators=[MinValueValidator(0.0)])


class Technology(models.Model):
    name = models.CharField(max_length=50)
    production_time_h = models.FloatField(validators=[MinValueValidator(0.0)])
    recipe = models.CharField(max_length=100)


class Stock(models.Model):
    poss = models.IntegerField(primary_key=True)
    item_id = models.IntegerField()
    quantity = models.FloatField(default=0, validators=[MinValueValidator(0.0)])
    placement_time = models.DateTimeField()
    placer = models.CharField(max_length=30)
    expiration_date = models.DateTimeField()
    # is_product - we can differentiate products id and raw materials id
    is_product = models.BooleanField(null=False)


class NutritionalValues(models.Model):
    protein = models.FloatField(validators=[MinValueValidator(0.0)])
    carbohydrate = models.FloatField(validators=[MinValueValidator(0.0)])
    carbohydrate_of_witch_sugars = models.FloatField(validators=[MinValueValidator(0.0)])
    salt = models.FloatField(validators=[MinValueValidator(0.0)])
    fat = models.FloatField(validators=[MinValueValidator(0.0)])
    fat_of_witch_saturates = models.FloatField(validators=[MinValueValidator(0.0)])
    energy = models.FloatField(validators=[MinValueValidator(0.0)])
    product_id = models.IntegerField(unique=True)


class RawMaterials(models.Model):
    # raw material id
    rmid = models.AutoField(primary_key=True, auto_created=True)
    name = models.CharField(max_length=40)
    quantity_in_stock = models.IntegerField(default=0)
    unit = models.CharField(max_length=5)


class Suppliers(models.Model):
    sid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    nip = models.IntegerField(unique=True)
    contact = models.CharField(max_length=12)
    bank_account = models.IntegerField()


class Orders(models.Model):
    cid = models.IntegerField()
    pid = models.IntegerField()
    quantity = models.FloatField(validators=[MinValueValidator(0.0)])
    price = models.FloatField(validators=[MinValueValidator(0.0)])
    total_amount = models.FloatField(validators=[MinValueValidator(0.0)])
    delivery_method = models.CharField(max_length=15)
    dead_line = models.DateTimeField()
    is_done = models.BooleanField()


class Clients(models.Model):
    cid = models.IntegerField(primary_key=True)
    is_company = models.BooleanField()
    contact = models.CharField(max_length=12)
    name = models.CharField(max_length=60)
    nip = models.IntegerField()
    address = models.CharField(max_length=60)


class User(AbstractUser):
    # role 1 - client, normal user
    # role 2 - deliver
    # role 3 - worker
    role = models.IntegerField(default=1)
