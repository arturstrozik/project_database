from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.db import connection
import datetime

from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from .forms import NewOrderForm, SignUpForm, ChangeStockForm, AddProductForm, AddRawMaterial, OrderHandling
from django.views.generic.edit import FormView
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)

from .sql_queries import *
from django.db import transaction


def home(request):
    return render(request, "base.html")


@login_required()
def new_order(request):
    form = NewOrderForm()
    form.fields["client_id"].initial = request.user.id
    form.fields["client_id"].disabled = True
    if request.method == "POST":
        client_id = request.user.id
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM database_project_user where id = '{0}' and role = 1".format(
                    str(client_id)
                )
            )
            client = cursor.fetchone()
        if not client:
            messages.error(request, "Nie odnaleźliśmy Cię w naszej bazie klientów.")
            return render(request, "new_order.html", {"form": form})
        data = datetime.datetime.now()
        product = request.POST.get("product")
        quantity = request.POST.get("quantity")
        delivery = request.POST.get("delivery")
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT pid, price FROM database_project_products where name = '{0}'".format(
                    str(product)
                )
            )
            row = cursor.fetchone()
            if row is None:
                messages.error(request, "Nie wybrano produktu, lub produkt jest niedostępny.")
                return render(request, "new_order.html", {"form": form})
            product_id = row[0]
            price = row[1]
        sum_price = float(quantity) * float(price)
        time_change = datetime.timedelta(days=14)
        dead_line = data + time_change

        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO database_project_orders (cid, pid, quantity, price, total_amount, delivery_method, dead_line, is_done, status) "
                "VALUES ({0}, {1}, {2}, {3}, {4}, '{5}', '{6}', '{7}', '{8}')".format(
                    client_id,
                    product_id,
                    quantity,
                    price,
                    sum_price,
                    delivery,
                    dead_line,
                    str(False),
                    "Oczekujące"
                )
            )
        messages.success("Zamówienie zostało złożone.")
        return redirect("/")
    else:
        return render(request, "new_order.html", {"form": form})


@login_required
def stock(request):
    all = ()
    with connection.cursor() as cursor:
        if request.user.role == 1:
            cursor.execute(
                "(SELECT name, sum(quantity) "
                "FROM database_project_stock INNER JOIN database_project_products ON item_id=pid WHERE is_product=True "
                "GROUP BY name) "
                "ORDER BY name"
            )
        elif request.user.role == 2:
            cursor.execute(
                "(SELECT is_product, name, sum(quantity) "
                "FROM database_project_stock INNER JOIN database_project_products ON item_id=pid WHERE is_product=True "
                "GROUP BY name, is_product "
                "UNION "
                "SELECT is_product, name, sum(quantity) "
                "FROM database_project_stock INNER JOIN database_project_rawmaterials ON item_id=rmid WHERE is_product=False "
                "GROUP BY name, is_product) "
                "ORDER BY name"
            )
        elif request.user.role == 3:
            cursor.execute(
                "(SELECT poss, is_product, item_id, name, quantity, placement_time, placer, expiration_date "
                "FROM database_project_stock LEFT JOIN database_project_products ON item_id=pid WHERE is_product=True "
                "UNION "
                "SELECT poss, is_product, item_id, name, quantity, placement_time, placer, expiration_date "
                "FROM database_project_stock LEFT JOIN database_project_rawmaterials ON item_id=rmid WHERE is_product=False) "
                "ORDER BY poss"
            )
        else:
            messages.error(request, "Nie masz dostępu do magazynu. Skontaktuj się z supportem lub administratorem.")
            return render(request, "/", messages)
        for row in cursor.fetchall():
            all = all + (row,)
    context = {
        "all": all,
    }
    return render(request, "stock.html", context)


@login_required
def orders(request):
    all = ()
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, cid, pid, quantity, price, total_amount, delivery_method, dead_line, status "
            "FROM database_project_orders ORDER BY id"
        )
        for row in cursor.fetchall():
            all = all + (row,)
    context = {
        "all": all,
    }
    return render(request, "orders.html", context)


@login_required
def order_handling(request):
    if request.user.role != 3:
        messages.error(request, "To może zrobić tylko pracownik.")
        return redirect("/", messages)
    form = OrderHandling()
    if request.method == "GET":
        order_id = request.GET.get("order_id")
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT c.id, c.username, o.status FROM database_project_orders o "
                "INNER JOIN database_project_user c ON o.cid=c.id "
                "WHERE o.id=%s",
                [str(order_id)]
            )
            client_data = cursor.fetchone()
            try:
                form.fields["client_data"].initial = str(client_data[0]) + ", " + str(client_data[1])
                form.fields["client_data"].disabled = True
                form.fields["id"].initial = order_id
                form.fields["id"].disabled = True
                form.fields["status"].initial = client_data[2]
            except KeyError:
                messages.error(request, "Błędny formularz.")
                return redirect("/", messages)
    if request.method == "POST":
        status = request.POST.get("status")
        order_id = request.GET.get("order_id")
        if status is not None:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE database_project_orders set status=%s WHERE id=%s", [status, order_id]
                )
            return redirect(orders)
    return render(request, "order_handling.html", {"form": form})


def register(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            done = insert_new_user(make_password(form.cleaned_data.get("password1")),
                                   form.cleaned_data.get("username"),
                                   form.cleaned_data.get("first_name"),
                                   form.cleaned_data.get("last_name"),
                                   form.cleaned_data.get("email"))

            if done:
                messages.success(request, "Rejestracja zakończyła się pomyślnie. Teraz można się zalogować")
                return redirect('home')
            else:
                form = form
                return render(request, "registration/register.html", {"form": form})
        else:
            form = form
            return render(request, "registration/register.html", {"form": form})
    else:
        form = SignUpForm()
        return render(request, "registration/register.html", {"form": form})


def logout_user(request):
    logout(request)
    messages.success(request, "Następiło poprawne wylogowanie")
    return redirect("home")


@login_required
def change_stock(request):
    if request.user.role != 3:
        messages.error(request, "To może zrobić tylko pracownik.")
        return redirect(request.META["HTTP_REFERER"], messages)
    form = ChangeStockForm()
    if request.method == "GET":
        try:
            form.fields["poss"].initial = request.GET["possition"]
            form.fields["poss"].disabled = True
        except KeyError:
            pass
    if request.method == "POST":
        poss = request.GET.get("possition")
        item_id = request.POST.get("item_id")
        quantity = request.POST.get("quantity")
        placement_time = request.POST.get("placement_time")
        placer = request.user.username
        expiration_date = request.POST.get("expiration_date")
        is_product = request.POST.get("is_product", False)

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE database_project_stock set item_id=%s, quantity=%s, placement_time=%s, placer=%s, expiration_date=%s, is_product=%s where poss=%s",
                [
                    item_id,
                    quantity,
                    placement_time,
                    placer,
                    expiration_date,
                    str(is_product),
                    poss,
                ],
            )
        return redirect("/stock")
    form.fields["placer"].initial = request.user.username
    form.fields["placer"].disabled = True
    return render(request, "change_stock.html", {"form": form})


@login_required
@transaction.atomic
def add_product(request):
    save_point = transaction.savepoint()
    if request.user.role != 3:
        messages.error(request, "To może zrobić tylko pracownik.")
        return redirect(request.META["HTTP_REFERER"], messages)
    if request.method == "POST":
        name = request.POST.get("name")
        quantity_in_stock = request.POST.get("quantity_in_stock")
        unit = request.POST.get("unit")
        expiration_date_in_days = request.POST.get("expiration_date_in_days")
        price = request.POST.get("price")
        technology_name = request.POST.get("technology_name")
        production_time_h = request.POST.get("production_time_h")
        recipe = request.POST.get("recipe")
        protein = request.POST.get("protein")
        carbohydrate = request.POST.get("carbohydrate")
        carbohydrate_of_witch_sugars = request.POST.get("carbohydrate_of_witch_sugars")
        salt = request.POST.get("salt")
        fat = request.POST.get("fat")
        fat_of_witch_saturates = request.POST.get("fat_of_witch_saturates")
        energy = request.POST.get("energy")

        try:
            done = insert_product(name, float(quantity_in_stock), unit, int(expiration_date_in_days), float(price))
            tech_status = insert_technology(technology_name, production_time_h, recipe, done["pid"])
            nutr_status = insert_nutritionalvalues(protein, carbohydrate, carbohydrate_of_witch_sugars,
                                                   salt, fat, fat_of_witch_saturates, energy, done["pid"])
        except (Exception,):
            messages.error(request, "Coś poszło nie tak. Spróbuj ponownie.")
            form = AddProductForm()
            return render(request, "add_product.html", {"form": form})
        else:
            if done["status"] and tech_status and nutr_status:
                messages.success(request, "Produkt został pomyślnie dodany.")
                transaction.savepoint_commit(save_point)
                return redirect('home')
            else:
                messages.error(request, "Coś poszło nie tak. Spróbuj ponownie.")
                form = AddProductForm()
                transaction.savepoint_rollback(save_point)
                return render(request, "add_product.html", {"form": form})
    else:
        form = AddProductForm()
        transaction.savepoint_rollback(save_point)
        return render(request, "add_product.html",  {"form": form})


@login_required
def add_raw_material(request):
    if request.user.role != 3:
        messages.error(request, "To może zrobić tylko pracownik.")
        return redirect(request.META["HTTP_REFERER"], messages)
    if request.method == "POST":
        name = request.POST.get("name")
        unit = request.POST.get("unit")
        quantity = 0
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM database_project_rawmaterials WHERE name=%s",
                           [name])
            if len(cursor.fetchall()) > 0:
                messages.error(request, "Ten rodzaj materiału już jest w naszej bazie.")
                return redirect(request.META["HTTP_REFERER"], messages)
            cursor.execute("INSERT INTO database_project_rawmaterials (name, quantity_in_stock, unit) "
                           "VALUES (%s, %s, %s) ", [name, str(quantity), unit])
            messages.success(request, "Materiał dodany do bazy danych.")
            return redirect(request.META["HTTP_REFERER"], messages)
    form = AddRawMaterial()
    return render(request, "add_material.html", {"form": form})


@login_required
def delivery_declaration(request):
    # only for delivers
    if request.user.role != 2:
        messages.error(request, "To może zrobić tylko dostawca.")
        return redirect("/", messages)
    if request.method == "POST":
        list = request.POST.getlist('delivers')
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM database_project_deliverdeclaration WHERE sid=%s", [request.user.id])
            for element in list:
                cursor.execute("INSERT INTO database_project_deliverdeclaration (rmid, sid)"
                               "VALUES (%s, %s)",
                               [
                                   element,
                                   request.user.id,
                               ])
    materials = []
    declared = []
    with connection.cursor() as cursor:
        cursor.execute("SELECT rmid, name, quantity_in_stock, unit FROM database_project_rawmaterials")
        for row in cursor.fetchall():
            materials.append(row)
        cursor.execute("SELECT rmid FROM database_project_deliverdeclaration WHERE sid=%s", [request.user.id])
        for row in cursor.fetchall():
            declared.append(row[0])
    return render(request, "material_list.html", {"materials": materials, "declared": declared})

