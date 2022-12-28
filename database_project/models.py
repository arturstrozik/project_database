from django.db import models


class Products(models.Model):
    product_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=30)
    quantity_in_stock = models.IntegerField(default=0)
    unit = models.CharField(max_length=5)
    poss_in_stock = models.IntegerField()
    serial_number = models.DateTimeField()
    expiration_date = models.DateTimeField()


class Technology(models.Model):
    name = models.CharField(max_length=50)
    production_time_h = models.FloatField()
    recipe = models.CharField()


class Stock(models.Model):
    poss = models.IntegerField()
    item_id = models.IntegerField()
    quantity = models.FloatField(default=0)
    placement_time = models.DateField()
    placer = models.CharField(max_length=30)
    expiration_date = models.DateTimeField()
    # is_product - we can differentiate products id and raw materials id
    is_product = models.BooleanField(null=False)


class NutritionalValues(models.Model):
    protein = models.FloatField()
    carbohydrate = models.FloatField()
    carbohydrate_of_witch_sugars = models.FloatField()
    salt = models.FloatField()
    fat = models.FloatField()
    fat_of_witch_saturates = models.FloatField()
    energy = models.FloatField()
    product_id = models.IntegerField(unique=True)


class RawMaterials(models.Model):
    rmid = models.IntegerField(unique=True)
    name = models.CharField(max_length=40)
    quantity_in_stock = models.IntegerField(default=0)
    unit = models.CharField(max_length=5)
    sid = models.IntegerField()


class Supplier(models.Model):
    sid = models.IntegerField(unique=True)
    name = models.CharField(max_length=50, unique=True)


