from app.pylavor import Pylavor


class DishIngredient:
    database_name = "dish_ingredients_db.json"
    
    dish_ref_num = None
    ingredient_ref_num = None
    quantity = None
    
    def __init__(self, data) -> None:
        self.dish_ref_num = data["dish_ref_num"]
        self.ingredient_ref_num = data["ingredient_ref_num"]
        self.quantity = data["quantity"]
    
    @staticmethod
    def check_db_existing():
        exists = Pylavor.check_file_exists(f"data/{DishIngredient.database_name}")
        
        if not exists:
            Pylavor.create_folder("data")
            Pylavor.json_write("data", DishIngredient.database_name, {}, sanitation=False)
    
    def save(self):
        DishIngredient.check_db_existing()
        all_dish_ingredients = Pylavor.json_read("data", DishIngredient.database_name)
        
        # Use dish_ref_num as key, store list of ingredients
        if self.dish_ref_num not in all_dish_ingredients:
            all_dish_ingredients[self.dish_ref_num] = []
        
        # Check if ingredient already exists for this dish
        ingredients_list = all_dish_ingredients[self.dish_ref_num]
        found = False
        for i, item in enumerate(ingredients_list):
            if item["ingredient_ref_num"] == self.ingredient_ref_num:
                ingredients_list[i] = self.to_json()
                found = True
                break
        
        if not found:
            ingredients_list.append(self.to_json())
        
        all_dish_ingredients[self.dish_ref_num] = ingredients_list
        Pylavor.json_write("data", DishIngredient.database_name, all_dish_ingredients)
    
    @staticmethod
    def get_for_dish(dish_ref_num):
        """Get all ingredients for a dish"""
        DishIngredient.check_db_existing()
        all_dish_ingredients = Pylavor.json_read("data", DishIngredient.database_name)
        
        if dish_ref_num not in all_dish_ingredients:
            return []
        
        return all_dish_ingredients[dish_ref_num]
    
    @staticmethod
    def delete(dish_ref_num, ingredient_ref_num):
        """Delete an ingredient from a dish"""
        DishIngredient.check_db_existing()
        all_dish_ingredients = Pylavor.json_read("data", DishIngredient.database_name)
        
        if dish_ref_num not in all_dish_ingredients:
            return False
        
        ingredients_list = all_dish_ingredients[dish_ref_num]
        ingredients_list = [item for item in ingredients_list if item["ingredient_ref_num"] != ingredient_ref_num]
        
        all_dish_ingredients[dish_ref_num] = ingredients_list
        Pylavor.json_write("data", DishIngredient.database_name, all_dish_ingredients)
        return True
    
    @staticmethod
    def delete_all_for_dish(dish_ref_num):
        """Delete all ingredients for a dish"""
        DishIngredient.check_db_existing()
        all_dish_ingredients = Pylavor.json_read("data", DishIngredient.database_name)
        
        if dish_ref_num in all_dish_ingredients:
            del all_dish_ingredients[dish_ref_num]
            Pylavor.json_write("data", DishIngredient.database_name, all_dish_ingredients)
            return True
        return False
    
    def to_json(self):
        data_ = {
            "dish_ref_num": self.dish_ref_num,
            "ingredient_ref_num": self.ingredient_ref_num,
            "quantity": self.quantity
        }
        return data_

