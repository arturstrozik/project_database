from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from .additional_function import *
from django.db import connection
import datetime

from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from .forms import *
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
    if request.method == "POST":
        form = NewOrderForm(request.POST)
        form.fields["client_id"].initial = request.user.id
        form.fields["client_id"].disabled = True
        if not form.is_valid():
            print(form.errors)
            messages.error(request, "W formularzu są błędne dane.")
            return redirect("/", messages)
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
                    "Przyjęte"
                )
            )
        try:
            estimated_time = get_estimated_time()
        except(Exception,):
            estimated_time = None
        messages.success(request, "Zamówienie zostało złożone.")
        if estimated_time is not None:
            messages.success(request, "Zamówienie zostanie zrealizowane za {} roboczogodzin.".format(estimated_time))
        else:
            messages.success(request, "Wkrótce rozpoczniemy realizację twojego zamówienia.")
        return redirect("/")
    else:
        form = NewOrderForm()
        form.fields["client_id"].initial = request.user.id
        form.fields["client_id"].disabled = True

        return render(request, "new_order.html", {"form": form})


@login_required
def stock(request):
    all = ()
    with connection.cursor() as cursor:
        if check_users_role(request.user.id, 1):
            cursor.execute(
                "(SELECT name, sum(quantity) "
                "FROM database_project_stock INNER JOIN database_project_products ON item_id=pid WHERE is_product=True "
                "GROUP BY name) "
                "ORDER BY name"
            )
        elif check_users_role(request.user.id, 2):
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
        elif check_users_role(request.user.id, 3):
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
            return redirect("/", messages)
        for row in cursor.fetchall():
            all = all + (row,)
    context = {
        "all": all,
    }
    return render(request, "stock.html", context)


@login_required
def orders(request):
    if check_users_role(request.user.id, 3):
        all = ()
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, cid, pid, quantity, price, total_amount, delivery_method, dead_line, status, is_done "
                "FROM database_project_orders ORDER BY id"
            )
            for row in cursor.fetchall():
                all = all + (row,)
        context = {
            "all": all,
        }
        return render(request, "orders.html", context)
    if check_users_role(request.user.id, 1):
        all = ()
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT p.name, o.quantity, o.price, o.total_amount, o.delivery_method, o.dead_line, o.status, o.is_done "
                "FROM database_project_orders o INNER JOIN database_project_products p ON o.pid=p.pid WHERE o.cid = %s ORDER BY o.id",
                [request.user.id]
            )
            for row in cursor.fetchall():
                all = all + (row,)
        context = {
            "all": all,
        }
        return render(request, "clients_orders.html", context)
    messages.error(request, "To może zrobić tylko pracownik.")
    return redirect(request.META["HTTP_REFERER"], messages)


@login_required
def order_handling(request):
    if not check_users_role(request.user.id, 3):
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
        is_done = request.POST.get("is_done", False)
        if status is not None:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE database_project_orders set status=%s, is_done=%s WHERE id=%s", [status, is_done, order_id]
                )
            return redirect(orders)
    return render(request, "order_handling.html", {"form": form})


def register(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if not form.is_valid():
            form = form
            return render(request, "registration/register.html", {"form": form})

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
        form = SignUpForm()
        return render(request, "registration/register.html", {"form": form})


def logout_user(request):
    logout(request)
    messages.success(request, "Następiło poprawne wylogowanie")
    return redirect("home")


@login_required
def change_stock(request):
    if not check_users_role(request.user.id, 3):
        messages.error(request, "To może zrobić tylko pracownik.")
        return redirect(request.META["HTTP_REFERER"], messages)
    form = ChangeStockForm()
    if request.method == "GET":
        #form = ChangeStockForm(request.GET)
        # if not form.is_valid():
        #     messages.error(request, "W formularzu są błędne dane.")
        #     return redirect("/", messages)
        try:
            form.fields["poss"].initial = request.GET["possition"]
            form.fields["poss"].disabled = True
        except KeyError:
            pass
    if request.method == "POST":
        # form = ChangeStockForm(request.POST)
        # if not form.is_valid():
        #     messages.error(request, "W formularzu są błędne dane.")
        #     return redirect("/", messages)
        poss = request.GET.get("possition")
        item_id = request.POST.get("item_id")
        quantity = request.POST.get("quantity")
        placement_time = request.POST.get("placement_time")
        placer = request.user.username
        expiration_date = request.POST.get("expiration_date")
        is_product = request.POST.get("is_product", False)

        if float(quantity) < 0:
            messages.error(request, "Błąd w ilości produktu.")
            return redirect("/", messages)

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE database_project_stock SET "
                "item_id=%s, quantity=%s, placement_time=%s, placer=%s, expiration_date=%s, is_product=%s WHERE poss=%s "
                "AND (%s in (select pid from database_project_products) or %s in (select rmid from database_project_rawmaterials) or %s = 0)",
                [
                    item_id,
                    quantity,
                    placement_time,
                    placer,
                    expiration_date,
                    str(is_product),
                    poss,
                    item_id,
                    item_id,
                    item_id,
                ],
            )
        return redirect("/stock/")
    form.fields["placer"].initial = request.user.username
    form.fields["placer"].disabled = True
    return render(request, "change_stock.html", {"form": form})


@login_required
@transaction.atomic
def add_product(request):
    save_point = transaction.savepoint()
    if not check_users_role(request.user.id, 3):
        messages.error(request, "To może zrobić tylko pracownik.")
        return redirect(request.META["HTTP_REFERER"], messages)
    if request.method == "POST":
        form = AddProductForm(request.POST)
        if not form.is_valid():
            messages.error(request, "W formularzu są błędne dane.")
            return redirect("/", messages)
        name = request.POST.get("name")
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
            done = insert_product(name, unit, int(expiration_date_in_days), float(price))
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
        transaction.savepoint_rollback(save_point)
        form = AddProductForm()
        return render(request, "add_product.html",  {"form": form})


@login_required
def add_raw_material(request):
    if not check_users_role(request.user.id, 3):
        messages.error(request, "To może zrobić tylko pracownik.")
        return redirect(request.META["HTTP_REFERER"], messages)
    form = AddRawMaterial()
    if request.method == "POST":
        form = AddRawMaterial(request.POST)
        if not form.is_valid():
            messages.error(request, "W formularzu są błędne dane.")
            return redirect("/", messages)
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
    return render(request, "add_material.html", {"form": form})


@login_required
def delivery_declaration(request):
    # only for delivers
    if not check_users_role(request.user.id, 2):
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


@login_required
@transaction.atomic
def update_product(request, product_id=0):
    save_point = transaction.savepoint()
    if not check_users_role(request.user.id, 3):
        messages.error(request, "To może zrobić tylko pracownik.")
        return redirect(request.META["HTTP_REFERER"], messages)
    try:
        product_data = get_specific_products(product_id)
        technology_data = get_specific_technology(product_id)
        nutritionalvalues_data = get_specific_nutritionalvalues(product_id)
    except(Exception,):
        messages.error(request, "Wystąpił błąd. Spróbuj ponownie później.")
        return redirect('/home/')

    if request.method == "POST":
        form = UpdateProductForm(request.POST)
        if not form.is_valid():
            messages.error(request, "W formularzu są błędne dane.")
            return redirect("/", messages)
        name = request.POST.get("name")
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
            up_product = update_product_sql(int(product_id), name, unit, int(expiration_date_in_days), float(price))
            up_technology = update_technology_sql(technology_name, float(production_time_h), recipe, int(product_id))
            up_nutritionalvalues = update_nutritionalvalues_sql(float(protein), float(carbohydrate),
                                                                float(carbohydrate_of_witch_sugars), float(salt),
                                                                float(fat), float(fat_of_witch_saturates),
                                                                float(energy), int(product_id))
        except (Exception,):
            messages.error(request, "Coś poszło nie tak. Spróbuj ponownie.")
            form = clear_update_form(product_data, technology_data, nutritionalvalues_data)
            return render(request, "update_product.html", {"form": form, "name": product_data["name"]})
        else:
            if up_product and up_technology and up_nutritionalvalues:
                messages.success(request, "Produkt został pomyślnie zmodyfikowany.")
                transaction.savepoint_commit(save_point)
                return redirect('home')
            else:
                messages.error(request, "Coś poszło nie tak. Spróbuj ponownie.")
                form = clear_update_form(product_data, technology_data, nutritionalvalues_data)
                transaction.savepoint_rollback(save_point)
                return render(request, "update_product.html", {"form": form, "name": product_data["name"]})

    else:
        transaction.savepoint_rollback(save_point)
        form = clear_update_form(product_data, technology_data, nutritionalvalues_data)
        return render(request, "update_product.html",  {"form": form, "name": product_data["name"]})


@login_required
def select_product_for_update(request):
    if not check_users_role(request.user.id, 3):
        messages.error(request, "To może zrobić tylko pracownik.")
        return redirect(request.META["HTTP_REFERER"], messages)
    form = SelectProductForm()
    if request.method == "POST":
        form = SelectProductForm(request.POST)
        if not form.is_valid():
            messages.error(request, "W formularzu są błędne dane.")
            return redirect("/", messages)
        product_id = request.POST.get("product")
        return redirect('update_product', product_id=product_id)
    else:
        return render(request, "select_product.html",  {"form": form})


@login_required
@transaction.atomic
def delete_product(request):
    if not check_users_role(request.user.id, 3):
        messages.error(request, "To może zrobić tylko pracownik.")
        return redirect(request.META["HTTP_REFERER"], messages)
    save_point = transaction.savepoint()
    form = DeleteProductForm()
    if request.method == "POST":
        form = DeleteProductForm(request.POST)
        if not form.is_valid():
            messages.error(request, "W formularzu są błędne dane.")
            return redirect("/", messages)
        product_id = request.POST.get("product")
        try:
            check = check_quantity(product_id)
        except (Exception,):
            check = False

        if check:
            try:
                delete_status = delete_product_technology_nutritionalvalues(product_id)
            except(Exception,):
                delete_status = False

            if delete_status:
                transaction.savepoint_commit(save_point)
                messages.success(request, "Pomyślnie usunięto produkt.")
                return redirect('home')
            else:
                transaction.savepoint_rollback(save_point)
                messages.error(request, "Coś poszło nie tak, spróbuj ponownie później.")
                form = DeleteProductForm()
                transaction.savepoint_rollback(save_point)
                return render(request, "select_product.html", {"form": form})
        else:
            messages.error(request, "Możesz usunąć produkt, którego ilość wynosi 0.")
            transaction.savepoint_rollback(save_point)
            form = DeleteProductForm()
            return render(request, "select_product.html", {"form": form})
    else:
        transaction.savepoint_rollback(save_point)
        return render(request, "select_product.html",  {"form": form})


@login_required
def order_material(request):
    if not check_users_role(request.user.id, 3):
        messages.error(request, "To może zrobić tylko pracownik.")
        return redirect(request.META["HTTP_REFERER"], messages)
    form = ChoseRawMaterialToOrder()
    delivers = None
    if request.method == "POST":
        form = ChoseRawMaterialToOrder(request.POST)
        rmid = request.POST.get("raw_material")
        form.fields["raw_material"].initial = rmid
        if not form.is_valid():
            print(form.errors)
            messages.error(request, "W formularzu są błędne dane.")
            return redirect("/", messages)
        delivers = ()
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT name, nip, contact, bank_account, sid_id FROM database_project_suppliers "
                "INNER JOIN database_project_deliverdeclaration ON sid=sid_id WHERE rmid=%s",
                [rmid]
            )
            for row in cursor.fetchall():
                delivers = delivers + (row,)

    context = {
        "form": form,
        "delivers": delivers,
    }
    return render(request, "raw_material_delivers.html", context)


