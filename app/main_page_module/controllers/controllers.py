import json

# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, jsonify, send_file, Response, abort

# Import module forms
from app.main_page_module.forms import form_dicts
#from app.main_page_module.p_objects.note_o import N_obj


from wrappers import login_required
from app.pylavor import Pylavor
from app.main_page_module.other import Randoms
from app.main_page_module.p_objects.meal import Meal
from app.main_page_module.p_objects.dish import Dish
from app.main_page_module.p_objects.day_special_food import DaySpecialFood
from app.main_page_module.p_objects.ingredient import Ingredient
from app.main_page_module.p_objects.dish_ingredient import DishIngredient


from app import app

#import os
import re
import os
import zipfile
import io
import pathlib
from passlib.hash import sha512_crypt
from datetime import datetime


# Define the blueprint: 'auth', set its url prefix: app.url/auth
main_page_module = Blueprint('main_page_module', __name__, url_prefix='/')


@app.context_processor
def inject_to_every_page():
    
    return dict(Randoms=Randoms, datetime=datetime, Pylavor=Pylavor,
                Dish=Dish, Meal=Meal, DaySpecialFood=DaySpecialFood,
                Ingredient=Ingredient, DishIngredient=DishIngredient)


@main_page_module.route('/', methods=['GET'])
def index():
    return render_template("main_page_module/index.html")

@main_page_module.route('/weekly_print', methods=['GET'])
def weekly_print():
    return render_template("main_page_module/weekly_print.html")

@main_page_module.route('/dishes/', methods=['GET'])
@login_required
def dishes():    
    return render_template("main_page_module/dishes/dishes_all.html")

@main_page_module.route('/dishes_new/', methods=['GET', 'POST'])
@login_required
def dishes_new():
    form = form_dicts["Dish"]()

    if form.validate_on_submit():
        dish_ref_num = Dish.new_id()
        
        dish_data = {"dish_ref_num": dish_ref_num,
            "name": form.name.data,
            "type_": form.type_.data,
            "main_dish": form.main_dish.data,
            "need_sidedish": form.need_sidedish.data,
            "show_in_planner": form.show_in_planner.data
            }

        dish = Dish(dish_data)
        
        try:
            dish.save()
            flash('Jed uspešno shranjena!', 'success')
            return redirect(url_for("main_page_module.dishes_view", dish_ref_num=dish_ref_num))
            
        except Exception as e:
            print(e)
            flash('Napaka pri shranjenju jedi!', 'error')        
        
    
    for error in form.errors:
        print(error)
        flash(f'Invalid Data: {error}', 'error')    

    return render_template("main_page_module/dishes/dishes_new.html", form=form)


@main_page_module.route('/dishes_view/<dish_ref_num>', methods=['GET'])
def dishes_view(dish_ref_num):
    dish_data = Dish.get_one(dish_ref_num)
    
    if dish_data is False:
        flash(f'Jed ne obstaja.', 'error')
        return redirect(url_for('main_page_module.dishes'))            
    
    dish = Dish(dish_data)
    
    return render_template("main_page_module/dishes/dishes_view.html", dish=dish)

@main_page_module.route('/dishes_edit/', methods=['POST'])
@main_page_module.route('/dishes_edit/<dish_ref_num>', methods=['GET', 'POST'])
@login_required
def dishes_edit(dish_ref_num:str=None):
    form = form_dicts["Dish"]()
    
    if dish_ref_num == None:
        dish_ref_num = form.dish_ref_num.data
    else:
        form.dish_ref_num.data = dish_ref_num
    
    dish_data = Dish.get_one(dish_ref_num)
    
    if dish_data is False:
        flash(f'Jed ne obstaja.', 'error')
        return redirect(url_for('main_page_module.dishes'))

    dish = Dish(dish_data)

    # GET
    if request.method == 'GET':
        form.process(dish_ref_num = dish_data["dish_ref_num"],
                     name = dish_data["name"],
                     type_ = dish_data["type_"],
                     main_dish = dish_data["main_dish"],
                     need_sidedish = dish_data["need_sidedish"],
                     show_in_planner = dish_data["show_in_planner"])
    
    # POST
    if form.validate_on_submit():
        dish_data = {"dish_ref_num": dish_ref_num,
            "name": form.name.data,
            "type_": form.type_.data,
            "main_dish": form.main_dish.data,
            "need_sidedish": form.need_sidedish.data,
            "show_in_planner": form.show_in_planner.data}
        
        dish = Dish(dish_data)

        try:
            dish.save()
            
            flash('Jed uspešno shranjena!', 'success')
            return redirect(url_for("main_page_module.dishes_view", dish_ref_num=dish_ref_num))
            
        except Exception as e:
            print(e)
            flash('Napaka pri shranjenju jedi!', 'error')
        
    
    for field, errors in form.errors.items():
        print(f'Field: {field}')
        for error in errors:
            flash(f'Invalid Data for {field}: {error}', 'error')
    
    
    return render_template("main_page_module/dishes/dishes_edit.html", form=form, dish=dish)



@main_page_module.route('/meals/', methods=['GET'])
@login_required
def meals():    
    return render_template("main_page_module/meals/meals_all.html")

@main_page_module.route('/meals_new/', methods=['GET', 'POST'])
@login_required
def meals_new():
    form = form_dicts["Meal"]()

    if form.validate_on_submit():
        meal_data = {"meal_date": str(form.meal_date.data),
            "main_dish": form.main_dish.data,
            "side_dish": form.side_dish.data,
            "keep": form.keep.data
            }
        meal = Meal(meal_data)
        
        try:
            meal.save()
            flash('Obrok uspešno shranjen!', 'success')
            return redirect(url_for("main_page_module.meals_view", meal_date=meal_date))
            
        except Exception as e:
            print(e)
            flash('Napaka pri shranjenju obroka!', 'error')        
        
    
    for error in form.errors:
        print(error)
        flash(f'Invalid Data: {error}', 'error')    

    return render_template("main_page_module/meals/meals_new.html", form=form)


@main_page_module.route('/meals_view/<meal_date>', methods=['GET'])
def meals_view(meal_date):
    meal_data = Meal.get_one(meal_date)
    
    if meal_data is False:
        flash(f'Obrok ne obstaja.', 'error')
        return redirect(url_for('main_page_module.meals'))            
    
    return render_template("main_page_module/meals/meals_view.html", meal=meal_data)


@main_page_module.route('/meals_edit/', methods=['POST'])
@main_page_module.route('/meals_edit/<meal_date>', methods=['GET', 'POST'])
@login_required
def meals_edit(meal_date:str=None):
    form = form_dicts["Meal"]()
    
    if meal_date == None:
        meal_date = form.meal_date.data
    else:
        form.meal_date.data = meal_date
    
    meal_data = Meal.get_one(meal_date)
    
    if meal_data is False:
        flash(f'Obrok ne obstaja.', 'error')
        return redirect(url_for('main_page_module.meals'))

    meal = Meal(meal_data)

    # GET
    if request.method == 'GET':
        form.process(meal_date = datetime.strptime(meal_data["meal_date"], "%Y-%m-%d").date(),
                     main_dish = meal_data["main_dish"],
                     side_dish = meal_data["side_dish"],
                     keep = meal_data.get("keep", "0"))
    
    # POST
    if form.validate_on_submit():
        meal_date = str(meal_date)
        meal_data = {"meal_date": meal_date,
            "main_dish": form.main_dish.data,
            "side_dish": form.side_dish.data,
            "keep": form.keep.data}
        
        meal = Meal(meal_data)

        try:
            meal.save()
            
            flash('Obrok uspešno shranjen!', 'success')
            return redirect(url_for("main_page_module.meals_view", meal_date=meal_date))
            
        except Exception as e:
            print(e)
            flash('Napaka pri shranjenju obroka!', 'error')
        
    
    for field, errors in form.errors.items():
        print(f'Field: {field}')
        for error in errors:
            flash(f'Invalid Data for {field}: {error}', 'error')
    
    
    return render_template("main_page_module/meals/meals_edit.html", form=form, meal=meal)


@main_page_module.route('/meals_randomize/<meal_date>/<index_>', methods=['GET'])
@main_page_module.route('/meals_randomize/<meal_date>', methods=['GET'])
def meals_randomize(meal_date, index_=False):
    meal_data = Meal.get_one(meal_date)
    
    if meal_data is False:
        flash(f'Obrok ne obstaja.', 'error')
        return redirect(url_for('main_page_module.meals'))            
    
    meal = Meal(meal_data)
    meal.randomize()
    
    if index_:
        return redirect(url_for("main_page_module.index"))
    else:
        return render_template("main_page_module/meals/meals_view.html", meal=meal)



@main_page_module.route('/generate_week/<week>', methods=['GET'])
@login_required
def generate_week(week):
    Meal.generate_week(week)
    
    return redirect(url_for("main_page_module.index"))



# Set the route and accepted methods
@main_page_module.route('/login/', methods=['GET', 'POST'])
def login():
    if ('user_id' in session):
        return redirect(url_for("main_page_module.index"))
    
    # If sign in form is submitted
    form = form_dicts["Login"]()

    # Verify the sign in form
    if form.validate_on_submit():
        admin_username = app.config['ADMIN_USERNAME']
        admin_password = app.config['ADMIN_PASS_HASH']
        
        # Generate the password hash
        same_pass = sha512_crypt.verify(form.password.data, admin_password)

        if not same_pass or admin_username != form.username_or_email.data:
            error_msg = "Login napačen."
            flash(error_msg, 'error')
            
        else:
            session['user_id'] = 1
            
            #set permanent login, if selected
            if form.remember.data == True:
                session.permanent = True
    
            error_msg = "Dobrodošel!"
            flash(error_msg, 'success')
            
            return redirect(url_for('main_page_module.index'))
    
        

    for field, errors in form.errors.items():
        app.logger.warn(f"Field: {field}")      
        for error in errors:
            flash(f'Invalid Data for {field}: {error}', 'error')

    return render_template("main_page_module/auth/login.html", form=form)
        

@main_page_module.route('/logout/')
def logout():
    #session.pop("user_id", None)
    #session.permanent = False
    session.clear()
    flash('You have been logged out. Have a nice day!', 'success')

    return redirect(url_for("main_page_module.index"))


@main_page_module.route('/day_special_foods/', methods=['GET'])
@login_required
def day_special_foods():
    return render_template("main_page_module/day_special_foods/day_special_foods_all.html")


@main_page_module.route('/day_special_foods_new/', methods=['GET', 'POST'])
@login_required
def day_special_foods_new():
    form = form_dicts["DaySpecialFood"]()
    
    if form.validate_on_submit():
        special_food_data = {
            "day_of_week": int(form.day_of_week.data),
            "main_dish": form.main_dish.data,
            "side_dish": form.side_dish.data if form.side_dish.data else ""
        }
        
        special_food = DaySpecialFood(special_food_data)
        
        try:
            special_food.save()
            flash('Posebna jed za dan uspešno shranjena!', 'success')
            return redirect(url_for("main_page_module.day_special_foods"))
        except Exception as e:
            print(e)
            flash('Napaka pri shranjenju posebne jedi!', 'error')
    
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'Invalid Data for {field}: {error}', 'error')
    
    return render_template("main_page_module/day_special_foods/day_special_foods_edit.html", form=form, day_of_week=None)


@main_page_module.route('/day_special_foods_edit/<day_of_week>', methods=['GET', 'POST'])
@login_required
def day_special_foods_edit(day_of_week):
    form = form_dicts["DaySpecialFood"]()
    
    # Edit existing special food
    day_of_week = int(day_of_week)
    special_food_data = DaySpecialFood.get_one(day_of_week)
    
    if special_food_data is False:
        flash(f'Posebna jed za ta dan ne obstaja.', 'error')
        return redirect(url_for('main_page_module.day_special_foods'))
    
    # GET - populate form
    if request.method == 'GET':
        form.process(day_of_week=str(special_food_data["day_of_week"]),
                   main_dish=special_food_data.get("main_dish", ""),
                   side_dish=special_food_data.get("side_dish", ""))
    
    # POST - save changes
    if form.validate_on_submit():
        special_food_data = {
            "day_of_week": int(form.day_of_week.data),
            "main_dish": form.main_dish.data,
            "side_dish": form.side_dish.data if form.side_dish.data else ""
        }
        
        special_food = DaySpecialFood(special_food_data)
        
        try:
            special_food.save()
            flash('Posebna jed za dan uspešno shranjena!', 'success')
            return redirect(url_for("main_page_module.day_special_foods"))
        except Exception as e:
            print(e)
            flash('Napaka pri shranjenju posebne jedi!', 'error')
    
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'Invalid Data for {field}: {error}', 'error')
    
    return render_template("main_page_module/day_special_foods/day_special_foods_edit.html", form=form, day_of_week=day_of_week)


@main_page_module.route('/day_special_foods_delete/<day_of_week>', methods=['GET'])
@login_required
def day_special_foods_delete(day_of_week):
    try:
        day_of_week = int(day_of_week)
        if DaySpecialFood.delete(day_of_week):
            flash('Posebna jed za dan uspešno izbrisana!', 'success')
        else:
            flash('Posebna jed za ta dan ne obstaja.', 'error')
    except Exception as e:
        print(e)
        flash('Napaka pri brisanju posebne jedi!', 'error')
    
    return redirect(url_for("main_page_module.day_special_foods"))


@main_page_module.route('/meals_toggle_keep/<meal_date>', methods=['GET'])
@login_required
def meals_toggle_keep(meal_date):
    meal_data = Meal.get_one(meal_date)
    
    if meal_data is False:
        flash(f'Obrok ne obstaja. Najprej generirajte jedilnik.', 'error')
        return redirect(url_for('main_page_module.index'))
    
    # Toggle keep status
    current_keep = meal_data.get("keep", "0")
    new_keep = "1" if current_keep == "0" else "0"
    
    meal_data["keep"] = new_keep
    meal = Meal(meal_data)
    
    try:
        meal.save()
        status_text = "ohranjen" if new_keep == "1" else "ne ohranjen"
        flash(f'Obrok je sedaj {status_text} pri generiranju!', 'success')
    except Exception as e:
        print(e)
        flash('Napaka pri shranjenju obroka!', 'error')
    
    return redirect(url_for("main_page_module.index"))


@main_page_module.route('/ingredients/', methods=['GET'])
@login_required
def ingredients():
    return render_template("main_page_module/ingredients/ingredients_all.html")


@main_page_module.route('/ingredients_new/', methods=['GET', 'POST'])
@login_required
def ingredients_new():
    form = form_dicts["Ingredient"]()
    
    if form.validate_on_submit():
        ingredient_ref_num = Ingredient.new_id()
        
        ingredient_data = {
            "ingredient_ref_num": ingredient_ref_num,
            "name": form.name.data,
            "unit_type": form.unit_type.data
        }
        
        ingredient = Ingredient(ingredient_data)
        
        try:
            ingredient.save()
            flash('Sestavina uspešno shranjena!', 'success')
            return redirect(url_for("main_page_module.ingredients"))
        except Exception as e:
            print(e)
            flash('Napaka pri shranjenju sestavine!', 'error')
    
    for error in form.errors:
        print(error)
        flash(f'Invalid Data: {error}', 'error')
    
    return render_template("main_page_module/ingredients/ingredients_new.html", form=form)


@main_page_module.route('/ingredients_view/<ingredient_ref_num>', methods=['GET'])
def ingredients_view(ingredient_ref_num):
    ingredient_data = Ingredient.get_one(ingredient_ref_num)
    
    if ingredient_data is False:
        flash(f'Sestavina ne obstaja.', 'error')
        return redirect(url_for('main_page_module.ingredients'))
    
    ingredient = Ingredient(ingredient_data)
    
    return render_template("main_page_module/ingredients/ingredients_view.html", ingredient=ingredient)


@main_page_module.route('/ingredients_edit/', methods=['POST'])
@main_page_module.route('/ingredients_edit/<ingredient_ref_num>', methods=['GET', 'POST'])
@login_required
def ingredients_edit(ingredient_ref_num:str=None):
    form = form_dicts["Ingredient"]()
    
    if ingredient_ref_num == None:
        ingredient_ref_num = form.ingredient_ref_num.data
    else:
        form.ingredient_ref_num.data = ingredient_ref_num
    
    ingredient_data = Ingredient.get_one(ingredient_ref_num)
    
    if ingredient_data is False:
        flash(f'Sestavina ne obstaja.', 'error')
        return redirect(url_for('main_page_module.ingredients'))
    
    ingredient = Ingredient(ingredient_data)
    
    # GET
    if request.method == 'GET':
        form.process(ingredient_ref_num=ingredient_data["ingredient_ref_num"],
                     name=ingredient_data["name"],
                     unit_type=ingredient_data["unit_type"])
    
    # POST
    if form.validate_on_submit():
        ingredient_data = {
            "ingredient_ref_num": ingredient_ref_num,
            "name": form.name.data,
            "unit_type": form.unit_type.data
        }
        
        ingredient = Ingredient(ingredient_data)
        
        try:
            ingredient.save()
            flash('Sestavina uspešno shranjena!', 'success')
            return redirect(url_for("main_page_module.ingredients_view", ingredient_ref_num=ingredient_ref_num))
        except Exception as e:
            print(e)
            flash('Napaka pri shranjenju sestavine!', 'error')
    
    for field, errors in form.errors.items():
        print(f'Field: {field}')
        for error in errors:
            flash(f'Invalid Data for {field}: {error}', 'error')
    
    return render_template("main_page_module/ingredients/ingredients_edit.html", form=form, ingredient=ingredient)


@main_page_module.route('/dish_ingredients_add/<dish_ref_num>', methods=['GET', 'POST'])
@login_required
def dish_ingredients_add(dish_ref_num):
    form = form_dicts["DishIngredient"]()
    
    dish_data = Dish.get_one(dish_ref_num)
    if dish_data is False:
        flash(f'Jed ne obstaja.', 'error')
        return redirect(url_for('main_page_module.dishes'))
    
    if form.validate_on_submit():
        dish_ingredient_data = {
            "dish_ref_num": dish_ref_num,
            "ingredient_ref_num": form.ingredient_ref_num.data,
            "quantity": form.quantity.data
        }
        
        dish_ingredient = DishIngredient(dish_ingredient_data)
        
        try:
            dish_ingredient.save()
            flash('Sestavina uspešno dodana jedi!', 'success')
            return redirect(url_for("main_page_module.dishes_view", dish_ref_num=dish_ref_num))
        except Exception as e:
            print(e)
            flash('Napaka pri dodajanju sestavine!', 'error')
    
    for error in form.errors:
        print(error)
        flash(f'Invalid Data: {error}', 'error')
    
    return render_template("main_page_module/dishes/dish_ingredients_add.html", form=form, dish_ref_num=dish_ref_num)


@main_page_module.route('/dish_ingredients_delete/<dish_ref_num>/<ingredient_ref_num>', methods=['GET'])
@login_required
def dish_ingredients_delete(dish_ref_num, ingredient_ref_num):
    try:
        if DishIngredient.delete(dish_ref_num, ingredient_ref_num):
            flash('Sestavina uspešno izbrisana iz jedi!', 'success')
        else:
            flash('Sestavina ne obstaja.', 'error')
    except Exception as e:
        print(e)
        flash('Napaka pri brisanju sestavine!', 'error')
    
    return redirect(url_for("main_page_module.dishes_view", dish_ref_num=dish_ref_num))


@main_page_module.route('/chopping_list/<week>', methods=['GET'])
@login_required
def chopping_list(week):
    """Generate chopping list for a week"""
    dates = Meal.get_week_dates(int(week))
    
    # Collect all ingredients for the week
    ingredients_dict = {}  # {ingredient_ref_num: {"ingredient": {...}, "total_quantity": "..."}}
    
    for date_ in dates:
        meal_data = Meal.get_one(date_)
        if meal_data:
            # Get main dish ingredients
            main_dish = meal_data.get("main_dish")
            if main_dish:
                dish_ingredients = DishIngredient.get_for_dish(main_dish)
                for di in dish_ingredients:
                    ing_id = di["ingredient_ref_num"]
                    ingredient_data = Ingredient.get_one(ing_id)
                    if ingredient_data:
                        if ing_id not in ingredients_dict:
                            ingredients_dict[ing_id] = {
                                "ingredient": ingredient_data,
                                "quantities": []
                            }
                        ingredients_dict[ing_id]["quantities"].append(di["quantity"])
            
            # Get side dish ingredients
            side_dish = meal_data.get("side_dish")
            if side_dish:
                dish_ingredients = DishIngredient.get_for_dish(side_dish)
                for di in dish_ingredients:
                    ing_id = di["ingredient_ref_num"]
                    ingredient_data = Ingredient.get_one(ing_id)
                    if ingredient_data:
                        if ing_id not in ingredients_dict:
                            ingredients_dict[ing_id] = {
                                "ingredient": ingredient_data,
                                "quantities": []
                            }
                        ingredients_dict[ing_id]["quantities"].append(di["quantity"])
    
    # Process quantities (for now just list them, could sum them if they're numeric)
    for ing_id, data in ingredients_dict.items():
        data["total_quantity"] = ", ".join(data["quantities"])
    
    return render_template("main_page_module/chopping_list.html", 
                          ingredients_dict=ingredients_dict, 
                          week=int(week),
                          dates=dates)