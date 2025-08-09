from app.pylavor import Pylavor
import glob
import os
import itertools
from PIL import Image
from os.path import exists
import datetime
from flask import url_for, session

import random
import string

from app import app



class Dish:
    database_name = "dishes_db.json"
    
    dish_ref_num = None
    
    name = None
    type_ = None # vegi, meat
    main_dish = None
    need_sidedish = None
    show_in_planner = None

    
    def __init__(self, dish_data) -> None:
        self.dish_ref_num = dish_data["dish_ref_num"]
        self.name = dish_data["name"]
        self.type_ = dish_data["type_"]
        self.main_dish = dish_data["main_dish"]
        self.need_sidedish = dish_data["need_sidedish"]
        self.show_in_planner = dish_data["show_in_planner"]
    
    # Dish
    @staticmethod
    def check_db_existing():
        exists = Pylavor.check_file_exists(f"data/{Dish.database_name}")
        
        if not exists:
            Pylavor.create_folder("data")
            Pylavor.json_write("data", Dish.database_name, {}, sanitation=False)
            
        

    # Dish
    @staticmethod
    def new_id():
        all_dishes = Pylavor.json_read("data", Dish.database_name)
        new_dish_id = "XXXXX"
        
        while True:
            new_dish_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            if not new_dish_id in all_dishes:
                break
        
        return new_dish_id
    
    # Dish
    def save(self):
        all_dishes = Pylavor.json_read("data", Dish.database_name)

        all_dishes[self.dish_ref_num] = self.to_json()
        
        Pylavor.json_write("data", Dish.database_name, all_dishes)    
    
    # Dish
    @staticmethod
    def get_one(dish_ref_num):
        all_dishes = Pylavor.json_read("data", Dish.database_name)

        if dish_ref_num not in all_dishes:
            return False

        return all_dishes[dish_ref_num]

    # Dish
    @staticmethod
    def get_all(type_="all", limit=0, planner_calc=False):
        Dish.check_db_existing()
     
        all_dishes = Pylavor.json_read("data", Dish.database_name)
        
        if planner_calc == True:
            all_dishes = {k: v for k, v in all_dishes.items() if v["show_in_planner"] == "1"}

        if type_ != "all":
            if type_.startswith("not_"):
                type_ = type_[4:]
                all_dishes = {k: v for k, v in all_dishes.items() if v["main_dish"] != type_}
            else:
                all_dishes = {k: v for k, v in all_dishes.items() if v["main_dish"] == type_}
        
        sorted_dishes = dict(sorted(all_dishes.items(), key=lambda item: item[1]["name"], reverse=True))
        
        if limit != 0:
            return dict(itertools.islice(sorted_dishes.items(), limit))
        else:
            return sorted_dishes
    
    # Dish
    def to_json(self):
        data_ = {"dish_ref_num": self.dish_ref_num,
                 "name": self.name,
                 "type_": self.type_,
                 "main_dish": self.main_dish,
                 "need_sidedish": self.need_sidedish,
                 "show_in_planner": self.show_in_planner
            }

        return data_
    
    
    # Dish
    @staticmethod
    def yes_no(yes_no):
        if yes_no == 1 or yes_no == "1" or yes_no == True:
            return "Da"
        else:
            return "Ne"
        
    # Dish
    @staticmethod
    def types(type_=False):
        types_ = {
            "Mesno": "meat",
            "Vegetarjansko": "vegetarian",
            "Vegansko": "Vegansko"
        }
        
        if type_ != False:
            return next((k for k, v in types_.items() if v == type_), None)        

        return types_
