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
        #self.helper.form_action = reverse("new_order")
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
        self.fields["product"].choices = tuple(product_tuple)
        self.helper.form_method = "POST"
        self.helper.add_input(Submit("submit", "Zamów"))

    client_id = forms.IntegerField(label="Twoje ID", min_value=0)
    quantity = forms.FloatField(label="Podaj ilość", min_value=0)
    product = forms.ChoiceField(label="Produkt")

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
        #self.helper.form_action = reverse("change_stock")
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
        #self.helper.form_action = reverse("add_product")
        self.helper.form_method = "POST"
        self.helper.add_input(Submit("submit", "Dodaj"))

    name = forms.CharField(label="Nazwa produktu", max_length=30)
    unit = forms.CharField(label="Jednostka", max_length=5)
    expiration_date_in_days = forms.IntegerField(label="Okres trwałości (w dniach)", validators=[MinValueValidator(0)])
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
        #self.helper.form_action = reverse("add_material")
        self.helper.form_method = "POST"
        self.helper.add_input(Submit("submit", "Dodaj"))

    name = forms.CharField(label="Nazwa materiału", max_length=30)
    unit = forms.CharField(label="Jednostka", max_length=5)


class OrderHandling(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        #self.helper.form_action = reverse("order_handling")
        self.helper.form_method = "POST"
        self.helper.add_input(Submit("submit", "Aktualizuj"))

    id = forms.IntegerField(label="ID zamówienia")
    client_data = forms.CharField(label="Klient")
    STATUS = (
        ("Przyjęte", "Przyjęte"),
        ("Oczekujące", "Oczekujące"),
        ("W produkcji", "W produkcji"),
        ("Przygotowywanie do wysyłki", "Przygotowywanie do wysyłki"),
        ("Gotowe do wysyłki", "Gotowe do wysyłki"),
        ("Wysłane", "Wysłane"),
    )
    status = forms.ChoiceField(
        choices=STATUS,
        initial="Przyjęte",
        label="Status zamówenia",
    )
    is_done = forms.BooleanField(
        label="Produkt jest już gotowy", required=False
    )


class UpdateProductForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        #self.helper.form_action = reverse("update_product", kwargs={'product_id': 1})
        self.helper.form_method = "POST"
        self.helper.add_input(Submit("submit", "Zmień"))

    name = forms.CharField(label="Nazwa produktu", max_length=30)
    unit = forms.CharField(label="Jednostka", max_length=5)
    expiration_date_in_days = forms.IntegerField(label="Okres trwałości (w dniach)", validators=[MinValueValidator(0)])
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
        #self.helper.form_action = reverse("select_product_for_update")
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
        #self.helper.form_action = reverse("delete_product")
        self.helper.form_method = "POST"
        self.helper.add_input(Submit("submit", "Usuń"))

    product = forms.ChoiceField(
        label="Wybierz produkt",
    )


class ChoseRawMaterialToOrder(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        #self.helper.form_action = reverse("order_material")
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT rmid, name, quantity_in_stock, unit FROM database_project_rawmaterials ORDER BY rmid"
            )
            raw_material_list = cursor.fetchall()
        raw_material_tuple = (("0", "Wybierz materiał"), )
        for row in raw_material_list:
            raw_material_tuple = raw_material_tuple + (
                (
                    str(row[0]),
                    str(row[0])
                    + " "
                    + str(row[1])
                    + " dostępne: "
                    + str(row[2])
                    + str(row[3]),
                ),
            )
        self.fields["raw_material"].choices = tuple(raw_material_tuple)
        self.helper.form_method = "POST"
        self.helper.add_input(Submit("submit", "Wyszukaj dostawców"))

    raw_material = forms.ChoiceField(label="Wybierz materiał",
                                     widget=forms.Select(attrs={'onchange': 'submit.click();'}))
