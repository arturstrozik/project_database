from datetime import datetime

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.urls import reverse

import database_project.models
from django.db import connection
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import User


class NewOrderForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = reverse("new_order")
        self.helper.form_method = "POST"
        self.helper.add_input(Submit("submit", "Zamów"))

    client_id = forms.IntegerField(label="Twoje ID", min_value=0)
    quantity = forms.FloatField(label="Podaj ilość", min_value=0)

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT name, price, quantity_in_stock, unit unit FROM database_project_products"
        )
        product_list = cursor.fetchall()
    product_tuple = ()
    for row in product_list:
        product_tuple = product_tuple + (
            (
                str(row[0]),
                str(row[0])
                + " "
                + str(row[1])
                + "zł/"
                + str(row[3])
                + " dostępne: "
                + str(row[2])
                + str(row[3]),
            ),
        )
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


class SignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        )


class ChangeStockForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = reverse("change_stock")
        self.helper.form_method = "POST"
        self.helper.add_input(Submit("submit", "Potwierdź"))

    poss = forms.IntegerField(label="Pozycja w magazynie")
    item_id = forms.IntegerField(label="Numer ID towaru")
    quantity = forms.FloatField(label="Ilość towaru")
    placement_time = forms.DateTimeField(
        initial=datetime.now(), label="Czas złożenia towaru w magazynie"
    )
    placer = forms.CharField(max_length=30, label="Magazynier")
    expiration_date = forms.DateTimeField(
        initial=datetime.now(), label="Ważność towaru/do kiedy może być składowany"
    )
    is_product = forms.BooleanField(
        label="Towar jest produktem końcowym", required=False
    )
