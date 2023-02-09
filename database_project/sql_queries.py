from django.db import connection
import traceback
import datetime


def insert_new_user(password, username, first_name, last_name, email):
    done = False
    with connection.cursor() as cursor:
        sql = "INSERT INTO database_project_user (id, password, username, first_name, last_name, " \
              "email, date_joined, is_active, is_superuser, is_staff, role) " \
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        date_joined = datetime.datetime.now()
        max_val_sql = "SELECT max(id) AS val FROM database_project_user"
        cursor.execute(max_val_sql)
        max_val = cursor.fetchone()[0]

        # when tabel is empty max_val is None
        try:
            val = (max_val + 1, password, username, first_name, last_name, email, date_joined, True, False, False, 1)
        except TypeError:
            val = (1, password, username, first_name, last_name, email, date_joined, True, False, False, 1)

        is_username_sql = "SELECT * FROM database_project_user WHERE username = %s "
        if max_val is None:
            is_username = None
        else:
            cursor.execute(is_username_sql, [username])
            is_username = cursor.fetchone()

        if is_username is None:
            try:
                cursor.execute(sql, val)
                done = True
                return done
            except(Exception,):
                print("Error - insert_new_user function")
                traceback.print_exc()
                return done
        else:
            print("Nie może być 2 użytkowników o tej samej nazwie.")
            return done


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
    done = False
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
                return done

            try:
                cursor.execute(sql, val)
                done = True
                return done
            except(Exception,):
                print("Error - insert_nutritionalvalues function")
                traceback.print_exc()
                return done
        else:
            print("You can't add nutritional values to the same product")
            return done


def insert_product(name: str, unit: str, expiration_date: int, price: float):
    # expiration_date is the number of days the product is fit for consumption
    done = {"status": False, "pid": 0}
    with connection.cursor() as cursor:
        max_val_sql = "SELECT max(pid) AS val FROM database_project_products"
        cursor.execute(max_val_sql)
        max_val = cursor.fetchone()[0]
        sql = "INSERT INTO database_project_products (pid, name, quantity_in_stock, unit, " \
              " serial_number, expiration_date_in_days, price) VALUES (%s, %s, %s, %s, %s, %s, %s)"
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
                val = (max_val + 1, name, 0, unit, serial_number, expiration_date, price)
            except TypeError:
                val = (1, name, 0, unit, serial_number, expiration_date, price)
            try:
                cursor.execute(sql, val)
                done["status"] = True
                done["pid"] = val[0]
                return done
            except(Exception,):
                print("Error - insert_product function")
                traceback.print_exc()
                return done
        else:
            print("You can't add product with the same pid")
            return done


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


def insert_technology(name: str, production_time_h: float, recipe: str, product_id: int):
    done = False
    with connection.cursor() as cursor:
        max_val_sql = "SELECT max(id) AS val FROM database_project_technology"
        cursor.execute(max_val_sql)
        max_val = cursor.fetchone()[0]
        sql = (
            "INSERT INTO database_project_technology (id, name, production_time_h, recipe, product_id) "
            "VALUES (%s, %s, %s, %s, %s)"
        )

        # when tabel is empty max_val is None
        try:
            val = (max_val + 1, name, production_time_h, recipe, product_id)
        except TypeError:
            val = (1, name, production_time_h, recipe, product_id)

        try:
            cursor.execute(sql, val)
            done = True
            return done
        except(Exception,):
            print("Error - insert_technology function")
            traceback.print_exc()
            return done


def get_products():
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "SELECT * FROM database_project_products"
            )
            product_list = cursor.fetchall()
        except (Exception,):
            pass

    return product_list


def get_specific_products(product_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM database_project_products WHERE pid = %s", [product_id]
        )
        product_list = cursor.fetchall()
        ready_dict = {"name": product_list[0][1], "unit": product_list[0][3],
                      "expiration": product_list[0][5], "price": product_list[0][6]}

    return ready_dict


def get_specific_technology(product_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM database_project_technology WHERE product_id = %s", [product_id]
        )
        technology_list = cursor.fetchall()
        ready_dict = {"name": technology_list[0][1], "time": technology_list[0][2], "recipe": technology_list[0][3]}

    return ready_dict


def get_specific_nutritionalvalues(product_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM database_project_nutritionalvalues WHERE product_id = %s", [product_id]
        )
        nutritionalvalues_list = cursor.fetchall()
        ready_dict = {"protein": nutritionalvalues_list[0][1], "carbohydrate": nutritionalvalues_list[0][2],
                      "carbohydrate_of_witch_sugars": nutritionalvalues_list[0][3], "salt": nutritionalvalues_list[0][4],
                      "fat": nutritionalvalues_list[0][5], "fat_of_witch_saturates": nutritionalvalues_list[0][6],
                      "energy": nutritionalvalues_list[0][7]}

    return ready_dict


def update_product_sql(pid: int, name: str, unit: str, expiration_date: int, price: float):
    # expiration_date is the number of days the product is fit for consumption
    done = False
    with connection.cursor() as cursor:
        sql = "UPDATE database_project_products SET name = %s, unit = %s, " \
              " expiration_date_in_days = %s, price = %s WHERE pid = %s"
        is_pid_sql = "SELECT * FROM database_project_products WHERE pid = %s "
        try:
            cursor.execute(is_pid_sql, [pid])
            is_pid = cursor.fetchone()
        except (Exception,):
            done = False
            return done

        if is_pid is not None:
            val = (name, unit, expiration_date, price, pid)
            try:
                cursor.execute(sql, val)
                done = True
                return done
            except(Exception,):
                print("Error - update_product function")
                traceback.print_exc()
                return done
        else:
            print("You can't update product - something went wrong")
            return done


def update_technology_sql(name: str, production_time_h: float, recipe: str, product_id: int):
    done = False
    with connection.cursor() as cursor:
        sql = (
            "UPDATE database_project_technology SET name = %s, production_time_h = %s, recipe = %s"
            "WHERE product_id = %s"
        )
        is_product_sql = "SELECT * FROM database_project_technology WHERE product_id = %s "
        try:
            cursor.execute(is_product_sql, [product_id])
            is_product = cursor.fetchone()
        except (Exception,):
            done = False
            return done

        if is_product is not None:
            val = (name, production_time_h, recipe, product_id)
            try:
                cursor.execute(sql, val)
                done = True
                return done
            except(Exception,):
                print("Error - update_technology function")
                traceback.print_exc()
                return done
        else:
            print("You can't update technology - something went wrong")
            return done


def update_nutritionalvalues_sql(
    protein: float,
    carbohydrate: float,
    carbohydrate_of_witch_sugars: float,
    salt: float,
    fat: float,
    fat_of_witch_saturates: float,
    energy: float,
    product_id: int,
):
    done = False
    with connection.cursor() as cursor:
        sql = (
            "UPDATE database_project_nutritionalvalues SET protein = %s, carbohydrate = %s,"
            " carbohydrate_of_witch_sugars = %s, salt = %s, fat= %s, fat_of_witch_saturates = %s, "
            "energy = %s WHERE product_id = %s"
        )
        is_product_id_sql = (
            "SELECT * FROM database_project_nutritionalvalues WHERE product_id = %s "
        )
        try:
            cursor.execute(is_product_id_sql, [product_id])
            is_product_id = cursor.fetchone()
        except (Exception,):
            done = False
            return done

        if is_product_id is not None:
            val = (
                protein,
                carbohydrate,
                carbohydrate_of_witch_sugars,
                salt,
                fat,
                fat_of_witch_saturates,
                energy,
                product_id,
            )

            try:
                cursor.execute(sql, val)
                done = True
                return done
            except(Exception,):
                print("Error - update_nutritionalvalues function")
                traceback.print_exc()
                return done
        else:
            print("You can't update nutritional values")
            return done


def check_quantity(product_id: int):
    with connection.cursor() as cursor:
        sql = (
            "SELECT quantity_in_stock FROM database_project_products WHERE pid = %s"
        )
        try:
            cursor.execute(sql, [product_id])
            quantity = cursor.fetchone()
            if quantity[0] == 0:
                return True
            else:
                return False
        except (Exception,):
            return False


def delete_product_technology_nutritionalvalues(product_id: int):
    with connection.cursor() as cursor:
        product_sql = (
            "DELETE FROM database_project_products WHERE pid = %s"
        )
        technology_sql = (
            "DELETE FROM database_project_technology WHERE product_id = %s"
        )
        nutritionalvalues_sql = (
            "DELETE FROM database_project_nutritionalvalues WHERE product_id = %s"
        )
        try:
            cursor.execute(product_sql, [product_id])
            cursor.execute(technology_sql, [product_id])
            cursor.execute(nutritionalvalues_sql, [product_id])
            return True
        except (Exception,):
            return False
