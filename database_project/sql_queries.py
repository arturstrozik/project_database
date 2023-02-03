from django.db import connection
import traceback
import datetime


def insert_client(is_company: bool, contact: str, name: str, nip: int, address: str):
    with connection.cursor() as cursor:
        max_val_sql = "SELECT max(id) AS val FROM database_project_clients"
        cursor.execute(max_val_sql)
        max_val = cursor.fetchone()[0]
        sql = (
            "INSERT INTO database_project_clients (id, is_company, contact, name, nip, address) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )

        # when tabel is empty max_val is None
        try:
            val = (max_val + 1, is_company, contact, name, nip, address)
        except TypeError:
            val = (1, is_company, contact, name, nip, address)

        try:
            cursor.execute(sql, val)
        except:
            print("Error - insert_client function")
            traceback.print_exc()


def insert_nutritionalvalues(
    protein: float,
    carbohydrate: float,
    carbohydrate_of_witch_sugars: float,
    salt: float,
    fat: float,
    fat_of_witch_saturates: float,
    energy: float,
    product_id: int,
):
    with connection.cursor() as cursor:
        max_val_sql = "SELECT max(id) AS val FROM database_project_nutritionalvalues"
        cursor.execute(max_val_sql)
        max_val = cursor.fetchone()[0]
        sql = (
            "INSERT INTO database_project_nutritionalvalues (id, protein, carbohydrate,"
            " carbohydrate_of_witch_sugars, salt, fat, fat_of_witch_saturates, energy, product_id) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        is_product_id_sql = (
            "SELECT * FROM database_project_nutritionalvalues WHERE product_id = %s "
        )
        cursor.execute(is_product_id_sql, [product_id])
        is_product_id = cursor.fetchone()

        if is_product_id is None:
            # when tabel is empty max_val is None
            try:
                val = (
                    max_val + 1,
                    protein,
                    carbohydrate,
                    carbohydrate_of_witch_sugars,
                    salt,
                    fat,
                    fat_of_witch_saturates,
                    energy,
                    product_id,
                )
            except TypeError:
                val = (
                    1,
                    protein,
                    carbohydrate,
                    carbohydrate_of_witch_sugars,
                    salt,
                    fat,
                    fat_of_witch_saturates,
                    energy,
                    product_id,
                )
            except KeyError:
                print("Key (product_id) already exists.")

            try:
                cursor.execute(sql, val)
            except:
                print("Error - insert_nutritionalvalues function")
                traceback.print_exc()
        else:
            print("You can't add nutritional values to the same product")


def insert_product(pid: int, name: str, quantity_in_stock: int, unit: str, poss_in_stock: int, expiration_date: int):
    # expiration_date is the number of days the product is fit for consumption
    done = False
    with connection.cursor() as cursor:
        max_val_sql = "SELECT max(pid) AS val FROM database_project_products"
        cursor.execute(max_val_sql)
        max_val = cursor.fetchone()[0]
        sql = "INSERT INTO database_project_products (id, pid, name, quantity_in_stock, unit, poss_in_stock," \
              " serial_number, expiration_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        serial_number = datetime.datetime.now()
        #expiration_date = serial_number + datetime.timedelta(days=expiration_date)
        is_pid_sql = "SELECT * FROM database_project_products WHERE pid = %s "
        if max_val is None:
            is_pid = None
        else:
            cursor.execute(is_pid_sql, [max_val+1])
            is_pid = cursor.fetchone()

        if is_pid is None:
            # when tabel is empty max_val is None
            try:
                val = (max_val + 1, name, quantity_in_stock, unit, serial_number, expiration_date, price)
            except TypeError:
                val = (1, name, quantity_in_stock, unit, serial_number, expiration_date, price)

            try:
                cursor.execute(sql, val)
                done = True
                return done
            except:
                print("Error - insert_product function")
                traceback.print_exc()
        else:
            print("You can't add product with the same pid")


def insert_rawmaterials(
    rmid: int, name: str, quantity_in_stock: int, unit: str, sid: int
):
    with connection.cursor() as cursor:
        max_val_sql = "SELECT max(id) AS val FROM database_project_rawmaterials"
        cursor.execute(max_val_sql)
        max_val = cursor.fetchone()[0]
        sql = (
            "INSERT INTO database_project_rawmaterials (id, rmid, name, quantity_in_stock, unit, sid) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )
        is_rmid_sql = "SELECT * FROM database_project_rawmaterials WHERE rmid = %s "
        cursor.execute(is_rmid_sql, [rmid])
        is_rmid = cursor.fetchone()

        if is_rmid is None:
            # when tabel is empty max_val is None
            try:
                val = (max_val + 1, rmid, name, quantity_in_stock, unit, sid)
            except TypeError:
                val = (1, rmid, name, quantity_in_stock, unit, sid)

            try:
                cursor.execute(sql, val)
            except:
                print("Error - insert_rawmaterials function")
                traceback.print_exc()
        else:
            print("You can't add raw material with the same rmid")


def insert_stock(
    poss: int,
    item_id: int,
    quantity: float,
    placer: str,
    expiration_date: int,
    is_product: bool,
):
    # expiration_date is the number of days the product is fit for consumption
    with connection.cursor() as cursor:
        max_val_sql = "SELECT max(id) AS val FROM database_project_stock"
        cursor.execute(max_val_sql)
        max_val = cursor.fetchone()[0]
        sql = (
            "INSERT INTO database_project_stock (id, poss, item_id, quantity, placement_time, placer,"
            " expiration_date, is_product) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        )
        placement_time = datetime.datetime.now()
        expiration_date = placement_time + datetime.timedelta(days=expiration_date)

        # when tabel is empty max_val is None
        try:
            val = (
                max_val + 1,
                poss,
                item_id,
                quantity,
                placement_time,
                placer,
                expiration_date,
                is_product,
            )
        except TypeError:
            val = (
                1,
                poss,
                item_id,
                quantity,
                placement_time,
                placer,
                expiration_date,
                is_product,
            )

        try:
            cursor.execute(sql, val)
        except:
            print("Error - insert_stock function")
            traceback.print_exc()


def insert_supplier(sid: int, name: str, nip: int, contact: str, bank_account: int):
    with connection.cursor() as cursor:
        max_val_sql = "SELECT max(id) AS val FROM database_project_suppliers"
        cursor.execute(max_val_sql)
        max_val = cursor.fetchone()[0]
        sql = (
            "INSERT INTO database_project_suppliers (id, sid, name, nip, contact, bank_account) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )
        is_sid_sql = "SELECT * FROM database_project_suppliers WHERE sid = %s "
        cursor.execute(is_sid_sql, [sid])
        is_sid = cursor.fetchone()
        is_name_sql = "SELECT * FROM database_project_suppliers WHERE name = %s "
        cursor.execute(is_name_sql, [name])
        is_name = cursor.fetchone()
        is_nip_sql = "SELECT * FROM database_project_suppliers WHERE nip = %s "
        cursor.execute(is_nip_sql, [nip])
        is_nip = cursor.fetchone()

        if (is_sid is None) and (is_name is None) and (is_nip is None):
            # when tabel is empty max_val is None
            try:
                val = (max_val + 1, sid, name, nip, contact, bank_account)
            except TypeError:
                val = (1, sid, name, nip, contact, bank_account)

            try:
                cursor.execute(sql, val)
            except:
                print("Error - insert_supplier function")
                traceback.print_exc()
        else:
            print("Values sid, name and nip have to be unique")


def insert_technology(name: str, production_time_h: float, recipe: str):
    with connection.cursor() as cursor:
        max_val_sql = "SELECT max(id) AS val FROM database_project_technology"
        cursor.execute(max_val_sql)
        max_val = cursor.fetchone()[0]
        sql = (
            "INSERT INTO database_project_technology (id, name, production_time_h, recipe) "
            "VALUES (%s, %s, %s, %s)"
        )

        # when tabel is empty max_val is None
        try:
            val = (max_val + 1, name, production_time_h, recipe)
        except TypeError:
            val = (1, name, production_time_h, recipe)

        try:
            cursor.execute(sql, val)
        except:
            print("Error - insert_technology function")
            traceback.print_exc()
