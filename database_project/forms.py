from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.urls import reverse

import database_project.models
from django.db import connection


class NewOrderForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = reverse("new_order")
        self.helper.form_method = "POST"
        self.helper.add_input(Submit("submit", "Szukaj"))

    client_id = forms.IntegerField(label="Twoje ID", min_value=0)
    quantity = forms.FloatField(label="Podaj ilość", min_value=0)

    with connection.cursor() as cursor:
        cursor.execute("SELECT name, price, unit FROM database_project_products")
        product_list = cursor.fetchall()
    product_tuple = ()
    for row in product_list:
        product_tuple = product_tuple + ((str(row[0]), str(row[0]) + " " + str(row[1]) + "zł/" + str(row[2])),)
    PRODUCT_CHOICE = tuple(product_tuple)
    product = forms.ChoiceField(
        choices=PRODUCT_CHOICE,
        label="Produkt",
    )

    DELIVERY_CHOICE = (
        ("DHL", "DHL"),
        ("inpost", "inpost"),
    )
    delivery = forms.ChoiceField(
        choices=DELIVERY_CHOICE,
        initial="inpost",
        label="Metoda dostawy",
    )
