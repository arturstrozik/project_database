from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render
from django.shortcuts import redirect

from django.db import connection
import datetime

from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from .forms import NewOrderForm, SignUpForm, ChangeStockForm
from django.views.generic.edit import FormView
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)


def home(request):
    return render(request, "base.html")


def new_order(request):
    if request.method == "POST":
        client_id = request.POST.get("client_id")
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM database_project_clients where id = '{0}'".format(str(client_id)))
            client = cursor.fetchone()
        if not client:
            form = NewOrderForm()
            return render(request, "new_order.html", {"form": form})
        data = datetime.datetime.now()
        product = request.POST.get("product")
        quantity = request.POST.get("quantity")
        delivery = request.POST.get("delivery")
        with connection.cursor() as cursor:
            cursor.execute("SELECT pid, price FROM database_project_products where name = '{0}'".format(str(product)))
            row = cursor.fetchone()
            product_id = row[0]
            price = row[1]
        sum_price = float(quantity) * float(price)
        time_change = datetime.timedelta(days=7)
        dead_line = data + time_change

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO database_project_orders (cid, pid, quantity, price, total_amount, delivery_method, dead_line) "
                           "VALUES ({0}, {1}, {2}, {3}, {4}, '{5}', '{6}')".format(client_id, product_id, quantity, price, sum_price, delivery, dead_line))
        return redirect("/")
    else:
        form = NewOrderForm()
        return render(request, "new_order.html",  {"form": form})


@login_required
def stock(request):
    ids, poss, item_ids, quantitys, placement_times, placers, exp_dates, is_products = [], [], [], [], [], [], [], []
    all = ()
    with connection.cursor() as cursor:
        cursor.execute("SELECT poss, item_id, quantity, placement_time, placer, expiration_date, is_product FROM database_project_stock ORDER BY poss")
        for row in cursor.fetchall():
            poss = poss.append(row[0])
            item_ids = item_ids.append(row[1])
            quantitys = quantitys.append(row[2])
            placement_times = placement_times.append(row[3])
            placers = placers.append(row[4])
            exp_dates = exp_dates.append(row[5])
            is_products = is_products.append(row[6])
            all = all + (row,)
    context = {
        "all": all,
    }
    return render(request, "stock.html", context)


def register(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        print("jest POST")
        if form.is_valid():
            print("jest valid")
            user = form.save()
            user.refresh_from_db()
            user.is_active = True
            user.first_name = form.cleaned_data.get("first_name")
            user.last_surname = form.cleaned_data.get("last_name")
            user.email = form.cleaned_data.get("email")
            print(user.email)
            user.save()
            current_site = get_current_site(request)

            return render(request, "registration/confirm.html", {'foo': 'bar'})
        else:
            form = form
            return render(request, "registration/register.html", {"form": form})
    else:
        form = SignUpForm()
        return render(request, "registration/register.html", {"form": form})


@login_required
def change_stock(request):
    if request.method == "POST":
        form = ChangeStockForm()
        if form.is_valid():
            return render(request, "change_stock.html", {"form": form})
    form = ChangeStockForm()
    form.fields["placer"].initial = request.user.username
    form.fields["placer"].disabled = True
    return render(request, "change_stock.html", {"form": form})
