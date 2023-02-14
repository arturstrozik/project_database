from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Products)
admin.site.register(Technology)
admin.site.register(NutritionalValues)
admin.site.register(Stock)
admin.site.register(RawMaterials)
admin.site.register(Suppliers)
admin.site.register(Clients)
admin.site.register(DeliverDeclaration)
admin.site.register(Orders)
admin.site.register(User)

