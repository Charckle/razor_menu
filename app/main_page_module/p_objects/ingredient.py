from app.pylavor import Pylavor
import random
import string


class Ingredient:
    database_name = "ingredients_db.json"
    
    ingredient_ref_num = None
    name = None
    unit_type = None  # liter, gram, piece, etc.
    
    def __init__(self, data) -> None:
        self.ingredient_ref_num = data["ingredient_ref_num"]
        self.name = data["name"]
        self.unit_type = data["unit_type"]
    
    @staticmethod
    def check_db_existing():
        exists = Pylavor.check_file_exists(f"data/{Ingredient.database_name}")
        
        if not exists:
            Pylavor.create_folder("data")
            Pylavor.json_write("data", Ingredient.database_name, {}, sanitation=False)
    
    @staticmethod
    def new_id():
        all_ingredients = Pylavor.json_read("data", Ingredient.database_name)
        new_ingredient_id = "XXXXX"
        
        while True:
            new_ingredient_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            if not new_ingredient_id in all_ingredients:
                break
        
        return new_ingredient_id
    
    def save(self):
        all_ingredients = Pylavor.json_read("data", Ingredient.database_name)
        
        all_ingredients[self.ingredient_ref_num] = self.to_json()
        
        Pylavor.json_write("data", Ingredient.database_name, all_ingredients)
    
    @staticmethod
    def get_one(ingredient_ref_num):
        Ingredient.check_db_existing()
        all_ingredients = Pylavor.json_read("data", Ingredient.database_name)
        
        if ingredient_ref_num not in all_ingredients:
            return False
        
        return all_ingredients[ingredient_ref_num]
    
    @staticmethod
    def get_all():
        Ingredient.check_db_existing()
        all_ingredients = Pylavor.json_read("data", Ingredient.database_name)
        return all_ingredients
    
    @staticmethod
    def delete(ingredient_ref_num):
        all_ingredients = Pylavor.json_read("data", Ingredient.database_name)
        
        if ingredient_ref_num in all_ingredients:
            del all_ingredients[ingredient_ref_num]
            Pylavor.json_write("data", Ingredient.database_name, all_ingredients)
            return True
        return False
    
    def to_json(self):
        data_ = {
            "ingredient_ref_num": self.ingredient_ref_num,
            "name": self.name,
            "unit_type": self.unit_type
        }
        return data_
    
    @staticmethod
    def get_unit_types():
        """Get available unit types"""
        return {
            "g": "gram",
            "kg": "kilogram",
            "ml": "mililiter",
            "l": "liter",
            "kom": "komad",
            "žlica": "žlica",
            "žlička": "žlička",
            "ščepec": "ščepec"
        }

