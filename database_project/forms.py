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
from django.core.validators import MinValueValidator
from .sql_queries import get_products


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
            "SELECT name, price, quantity_in_stock, unit FROM database_project_products"
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
        self.fields["username"].required = True
        self.fields["email"].required = True
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["password1"].required = True
        self.fields["password2"].required = True

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


class AddProductForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = reverse("add_product")
        self.helper.form_method = "POST"
        self.helper.add_input(Submit("submit", "Dodaj"))

    name = forms.CharField(label="Nazwa produktu", max_length=30)
    quantity_in_stock = forms.FloatField(label="Ilość")
    unit = forms.CharField(label="Jednostka", max_length=5)
    expiration_date_in_days = forms.IntegerField(label="Okres trwałości (w dniach)")
    price = forms.FloatField(label="Cena", validators=[MinValueValidator(0.0)])
    technology_name = forms.CharField(label="Nazwa technologi", max_length=50)
    production_time_h = forms.FloatField(label="Czas produkcji", validators=[MinValueValidator(0.0)])
    recipe = forms.CharField(label="Przepis", max_length=5000)
    protein = forms.FloatField(label="Białko", validators=[MinValueValidator(0.0)])
    carbohydrate = forms.FloatField(label="Węglowodany", validators=[MinValueValidator(0.0)])
    carbohydrate_of_witch_sugars = forms.FloatField(label="W tym cukry", validators=[MinValueValidator(0.0)])
    salt = forms.FloatField(label="Sól", validators=[MinValueValidator(0.0)])
    fat = forms.FloatField(label="Tłuszcz", validators=[MinValueValidator(0.0)])
    fat_of_witch_saturates = forms.FloatField(label="W tym nasycone", validators=[MinValueValidator(0.0)])
    energy = forms.FloatField(label="Energia", validators=[MinValueValidator(0.0)])


class AddRawMaterial(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = reverse("add_material")
        self.helper.form_method = "POST"
        self.helper.add_input(Submit("submit", "Dodaj"))

    name = forms.CharField(label="Nazwa materiału", max_length=30)
    unit = forms.CharField(label="Jednostka", max_length=5)


class OrderHandling(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = reverse("order_handling")
        self.helper.form_method = "POST"
        self.helper.add_input(Submit("submit", "Aktualizuj"))

    id = forms.IntegerField(label="ID zamówienia")
    client_data = forms.CharField(label="Klient")
    status = forms.CharField(max_length=40, label="Status zamówenia")


class UpdateProductForm(forms.Form):
    def __init__(self, product_data, technology_data, nutritionalvalues_data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.fields["name"].initial = product_data["name"]
        self.fields["unit"].initial = product_data["unit"]
        self.fields["expiration_date_in_days"].initial = product_data["expiration"]
        self.fields["price"].initial = product_data["price"]
        self.fields["technology_name"].initial = technology_data["name"]
        self.fields["production_time_h"].initial = technology_data["time"]
        self.fields["recipe"].initial = technology_data["recipe"]
        self.fields["protein"].initial = nutritionalvalues_data["protein"]
        self.fields["carbohydrate"].initial = nutritionalvalues_data["carbohydrate"]
        self.fields["carbohydrate_of_witch_sugars"].initial = nutritionalvalues_data["carbohydrate_of_witch_sugars"]
        self.fields["salt"].initial = nutritionalvalues_data["salt"]
        self.fields["fat"].initial = nutritionalvalues_data["fat"]
        self.fields["fat_of_witch_saturates"].initial = nutritionalvalues_data["fat_of_witch_saturates"]
        self.fields["energy"].initial = nutritionalvalues_data["energy"]
        self.helper.form_action = reverse("update_product",  kwargs={'product_id': 0})
        self.helper.form_method = "POST"
        self.helper.add_input(Submit("submit", "Zmień"))

    name = forms.CharField(label="Nazwa produktu", max_length=30)
    unit = forms.CharField(label="Jednostka", max_length=5)
    expiration_date_in_days = forms.IntegerField(label="Okres trwałości (w dniach)")
    price = forms.FloatField(label="Cena", validators=[MinValueValidator(0.0)])
    technology_name = forms.CharField(label="Nazwa technologi", max_length=50)
    production_time_h = forms.FloatField(label="Czas produkcji", validators=[MinValueValidator(0.0)])
    recipe = forms.CharField(label="Przepis", max_length=5000)
    protein = forms.FloatField(label="Białko", validators=[MinValueValidator(0.0)])
    carbohydrate = forms.FloatField(label="Węglowodany", validators=[MinValueValidator(0.0)])
    carbohydrate_of_witch_sugars = forms.FloatField(label="W tym cukry", validators=[MinValueValidator(0.0)])
    salt = forms.FloatField(label="Sól", validators=[MinValueValidator(0.0)])
    fat = forms.FloatField(label="Tłuszcz", validators=[MinValueValidator(0.0)])
    fat_of_witch_saturates = forms.FloatField(label="W tym nasycone", validators=[MinValueValidator(0.0)])
    energy = forms.FloatField(label="Energia", validators=[MinValueValidator(0.0)])


class SelectProductForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        product_list = get_products()
        product_tuple = ()
        for row in product_list:
            product_tuple = product_tuple + (
                (
                    str(row[0]),
                    str(row[1])
                    + " "
                    + str(row[6])
                    + "zł/"
                    + str(row[3])
                    + " dostępne: "
                    + str(row[2])
                    + str(row[3]),
                ),
            )
        self.fields["product"].choices = tuple(product_tuple)
        self.helper.form_action = reverse("select_product_for_update")
        self.helper.form_method = "POST"
        self.helper.add_input(Submit("submit", "Przejdź dalej"))

    product = forms.ChoiceField(
        label="Wybierz produkt",
    )


class DeleteProductForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        product_list = get_products()
        product_tuple = ()
        for row in product_list:
            product_tuple = product_tuple + (
                (
                    str(row[0]),
                    str(row[1])
                    + " "
                    + str(row[6])
                    + "zł/"
                    + str(row[3])
                    + " dostępne: "
                    + str(row[2])
                    + str(row[3]),
                ),
            )

        self.fields["product"].choices = tuple(product_tuple)
        self.helper.form_action = reverse("delete_product")
        self.helper.form_method = "POST"
        self.helper.add_input(Submit("submit", "Usuń"))

    product = forms.ChoiceField(
        label="Wybierz produkt",
    )
