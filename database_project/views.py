from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import redirect

from django.db import connection
import datetime
from .forms import NewOrderForm


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
        cursor.execute("SELECT id, poss, item_id, quantity, placement_time, placer, expiration_date, is_product FROM database_project_stock ORDER BY id")
        for row in cursor.fetchall():
            ids = ids.append(row[0])
            poss = poss.append(row[1])
            item_ids = item_ids.append(row[2])
            quantitys = quantitys.append(row[3])
            placement_times = placement_times.append(row[4])
            placers = placers.append(row[5])
            exp_dates = exp_dates.append(row[6])
            is_products = is_products.append(row[7])
            all = all + (row,)
    context = {
        "all": all,
    }
    return render(request, "stock.html", context)
