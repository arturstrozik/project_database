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

from .forms import NewOrderForm, SignUpForm, ChangeStockForm, AddProductForm
from django.views.generic.edit import FormView
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)

from .sql_queries import insert_product, insert_new_user


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
                "INSERT INTO database_project_orders (cid, pid, quantity, price, total_amount, delivery_method, dead_line, is_done) "
                "VALUES ({0}, {1}, {2}, {3}, {4}, '{5}', '{6}', '{7}')".format(
                    client_id,
                    product_id,
                    quantity,
                    price,
                    sum_price,
                    delivery,
                    dead_line,
                    str(False),
                )
            )
        return redirect("/")
    else:
        return render(request, "new_order.html", {"form": form})


@login_required
def stock(request):
    ids, poss, item_ids, quantitys, placement_times, placers, exp_dates, is_products = (
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )
    all = ()
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT poss, item_id, quantity, placement_time, placer, expiration_date, is_product "
            "FROM database_project_stock ORDER BY poss"
        )
        for row in cursor.fetchall():
            poss.append(row[0])
            item_ids.append(row[1])
            quantitys.append(row[2])
            placement_times.append(row[3])
            placers.append(row[4])
            exp_dates.append(row[5])
            is_products.append(row[6])
            all = all + (row,)
    context = {
        "all": all,
    }
    return render(request, "stock.html", context)


@login_required
def orders(request):
    ids, cids, pids, quantitys, prices, total_amounts, delivery_methods, dead_lines  = (
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )
    all = ()
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, cid, pid, quantity, price, total_amount, delivery_method, dead_line "
            "FROM database_project_orders ORDER BY id"
        )
        for row in cursor.fetchall():
            ids.append(row[0])
            cids.append(row[1])
            pids.append(row[2])
            quantitys.append(row[3])
            prices.append(row[4])
            total_amounts.append(row[5])
            delivery_methods.append(row[6])
            dead_lines.append(row[7])
            all = all + (row,)
    context = {
        "all": all,
    }
    return render(request, "orders.html", context)


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
        return redirect(request, "stock")
    form.fields["placer"].initial = request.user.username
    form.fields["placer"].disabled = True
    return render(request, "change_stock.html", {"form": form})


@login_required
def add_product(request):
    if request.method == "POST":
        if request.user.role != 3:
            messages.error(request, "To może zrobić tylko pracownik.")
            return redirect(request.META["HTTP_REFERER"], messages)
        name = request.POST.get("name")
        quantity_in_stock = request.POST.get("quantity_in_stock")
        unit = request.POST.get("unit")
        expiration_date_in_days = request.POST.get("expiration_date_in_days")
        price = request.POST.get("price")

        try:
            done = insert_product(name, float(quantity_in_stock), unit, int(expiration_date_in_days), float(price))
        except (Exception,):
            messages.error(request, "Coś poszło nie tak. Spróbuj ponownie.")
            form = AddProductForm()
            return render(request, "add_product.html", {"form": form})
        else:
            if done:
                messages.success(request, "Produkt został pomyślnie dodany.")
                return redirect('home')
            else:
                messages.error(request, "Coś poszło nie tak. Spróbuj ponownie.")
                form = AddProductForm()
                return render(request, "add_product.html", {"form": form})
    else:
        form = AddProductForm()
        return render(request, "add_product.html",  {"form": form})
