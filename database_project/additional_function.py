from database_project.forms import UpdateProductForm


def clear_update_form(product_data, technology_data, nutritionalvalues_data):
    form = UpdateProductForm()
    form.fields["name"].initial = product_data["name"]
    form.fields["unit"].initial = product_data["unit"]
    form.fields["expiration_date_in_days"].initial = product_data["expiration"]
    form.fields["price"].initial = product_data["price"]
    form.fields["technology_name"].initial = technology_data["name"]
    form.fields["production_time_h"].initial = technology_data["time"]
    form.fields["recipe"].initial = technology_data["recipe"]
    form.fields["protein"].initial = nutritionalvalues_data["protein"]
    form.fields["carbohydrate"].initial = nutritionalvalues_data["carbohydrate"]
    form.fields["carbohydrate_of_witch_sugars"].initial = nutritionalvalues_data["carbohydrate_of_witch_sugars"]
    form.fields["salt"].initial = nutritionalvalues_data["salt"]
    form.fields["fat"].initial = nutritionalvalues_data["fat"]
    form.fields["fat_of_witch_saturates"].initial = nutritionalvalues_data["fat_of_witch_saturates"]
    form.fields["energy"].initial = nutritionalvalues_data["energy"]

    return form
