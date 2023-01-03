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
        data = datetime.datetime.now()
        product = request.POST.get("product")
        quantity = request.POST.get("quantity")
        delivery = request.POST.get("delivery")
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, price FROM database_project_products where name = {0}".format(product))
            product_id = cursor.fetchone()[0]
            price = cursor.fetchone()[1]
        sum_price = float(quantity) * float(price)
        time_change = datetime.timedelta(days=7)
        dead_line = data + time_change

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO database_project_orders (cid, pid, quantity, price, total_amount, delivery_method, dead_line) "
                           "VALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6})".format(client_id, product_id, quantity, price, sum_price, delivery, dead_line))
        return redirect("/")
    else:
        form = NewOrderForm()
        return render(request, "new_order.html",  {"form": form})
