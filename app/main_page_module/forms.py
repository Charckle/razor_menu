# Import Form and RecaptchaField (optional)
from flask_wtf import FlaskForm # , RecaptchaField
from flask_wtf.file import FileField, MultipleFileField, FileAllowed, FileRequired

# Import Form elements such as TextField and BooleanField (optional)
from wtforms import BooleanField, IntegerField, StringField, TextAreaField, SelectField, \
     PasswordField, HiddenField, SubmitField, DateField, validators # BooleanField

# Import Form validators
from wtforms.validators import Email, EqualTo, ValidationError, InputRequired

from datetime import date


#email verification
import re
import os.path

from app.main_page_module.p_objects.dish import Dish
from app.main_page_module.p_objects.day_special_food import DaySpecialFood
from app.main_page_module.p_objects.ingredient import Ingredient



class DishForm(FlaskForm):    
    dish_ref_num = HiddenField('dish_ref_num', [validators.InputRequired(message='Dont fiddle around with the code!')])
    name = StringField('Ime', [validators.InputRequired(message='We need a name.'), validators.Length(max=150)])
    type_ = SelectField('Vrsta jedi:', [
        validators.InputRequired(message='You need to specify the main jed')], 
                         choices=[])    
    
    main_dish = SelectField(u'Ali je glavna jed?', [
        validators.InputRequired(message='You need to specify the time')], 
                         choices=[('1', 'Da'), ('0', 'Ne')])
    
    need_sidedish = SelectField(u'Potrebuje prilogo?', [
        validators.InputRequired(message='You need to specify the time')], 
                         choices=[('0', 'Ne'), ('1', 'Da')])      
    
    show_in_planner = SelectField(u'Naj se uporabi v avtomatski kalkulaciji?', [
        validators.InputRequired(message='You need to specify the time')], 
                         choices=[('1', 'Da'), ('0', 'Ne')])          
    
    
    
    submit = SubmitField('Dodaj Obrok')
    
    
    def __init__(self, *args, **kwargs):
        super(DishForm, self).__init__(*args, **kwargs)
        self.type_.choices = [[id_, name] for name, id_ in Dish.types().items()]


class MealForm(FlaskForm):    
    meal_date = DateField(
            'Datum obroka',
            validators=[InputRequired(message='We need a date.')],
            format='%Y-%m-%d',
            default=date.today
        )
    
    
    main_dish = SelectField('Glavna jed:', [
        validators.InputRequired(message='You need to specify the main jed')], 
                         choices=[])
    
    
    side_dish = SelectField('Priloga:', [
        validators.InputRequired(message='You need to specify the priloga')], 
                         choices=[('/', 'Brez')])
    
    keep = SelectField('Ohrani pri generiranju:', [
        validators.InputRequired(message='You need to specify if to keep')], 
                         choices=[('0', 'Ne'), ('1', 'Da')])
    
    
    submit = SubmitField('Dodaj Obrok')
    
    
    def __init__(self, *args, **kwargs):
        super(MealForm, self).__init__(*args, **kwargs)
        self.main_dish.choices = [[id_, data_["name"]] for id_, data_ in Dish.get_all(type_="1").items()]  
        self.side_dish.choices += [[id_, data_["name"]] for id_, data_ in Dish.get_all(type_="0").items()]    

class IngredientForm(FlaskForm):
    ingredient_ref_num = HiddenField('ingredient_ref_num', [validators.InputRequired(message='Dont fiddle around with the code!')])
    name = StringField('Ime', [validators.InputRequired(message='We need a name.'), validators.Length(max=150)])
    unit_type = SelectField('Enota:', [
        validators.InputRequired(message='You need to specify the unit type')], 
                         choices=[])
    
    submit = SubmitField('Shrani')
    
    def __init__(self, *args, **kwargs):
        super(IngredientForm, self).__init__(*args, **kwargs)
        self.unit_type.choices = [[id_, name] for id_, name in Ingredient.get_unit_types().items()]


class DishIngredientForm(FlaskForm):
    ingredient_ref_num = SelectField('Sestavina:', [
        validators.InputRequired(message='You need to select an ingredient')], 
                         choices=[])
    quantity = StringField('Količina', [validators.InputRequired(message='We need a quantity.'), validators.Length(max=50)])
    
    submit = SubmitField('Dodaj')
    
    def __init__(self, *args, **kwargs):
        super(DishIngredientForm, self).__init__(*args, **kwargs)
        # Get all ingredients and sort them alphabetically by name
        all_ingredients = Ingredient.get_all()
        sorted_ingredients = sorted(all_ingredients.items(), key=lambda x: x[1]["name"].lower())
        self.ingredient_ref_num.choices = [[id_, data_["name"] + " (" + data_.get("unit_type", "") + ")"] for id_, data_ in sorted_ingredients]


class DaySpecialFoodForm(FlaskForm):
    day_of_week = SelectField('Dan v tednu:', [
        validators.InputRequired(message='You need to specify the day of week')], 
                         choices=[
                             ('0', 'Ponedeljek'),
                             ('1', 'Torek'),
                             ('2', 'Sreda'),
                             ('3', 'Četrtek'),
                             ('4', 'Petek'),
                             ('5', 'Sobota'),
                             ('6', 'Nedelja')
                         ])
    
    main_dish = SelectField('Glavna jed:', [
        validators.InputRequired(message='You need to specify the main jed')], 
                         choices=[])
    
    side_dish = SelectField('Priloga:', 
                         choices=[('', 'Brez')])
    
    submit = SubmitField('Shrani')
    
    def __init__(self, *args, **kwargs):
        super(DaySpecialFoodForm, self).__init__(*args, **kwargs)
        self.main_dish.choices = [[id_, data_["name"]] for id_, data_ in Dish.get_all(type_="1").items()]  
        self.side_dish.choices += [[id_, data_["name"]] for id_, data_ in Dish.get_all(type_="0").items()]

class LoginForm(FlaskForm):
    username_or_email = StringField('Username or Email', [validators.InputRequired(message='Forgot your email address?')])
    password = PasswordField('Password', [validators.InputRequired(message='Must provide a password.')])
    remember = BooleanField()
    
    submit = SubmitField('Login')


 
form_dicts = {"Meal": MealForm,
              "Dish": DishForm,
              "Login": LoginForm,
              "DaySpecialFood": DaySpecialFoodForm,
              "Ingredient": IngredientForm,
              "DishIngredient": DishIngredientForm
              } 
