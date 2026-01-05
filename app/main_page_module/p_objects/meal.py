from app.pylavor import Pylavor
import glob
import os
import itertools
from PIL import Image
from os.path import exists
from datetime import date, timedelta, datetime

from flask import url_for, session

import random
import string

from app import app

from app.main_page_module.p_objects.dish import Dish
from app.main_page_module.p_objects.day_special_food import DaySpecialFood


def is_friday(date_):
    date_obj = datetime.strptime(date_, "%Y-%m-%d")
    
    # weekday(): Monday=0, Sunday=6
    
    return date_obj.weekday() == 4
    
    

class Meal:
    database_name = "meals_db.json"
    
    meal_date = None
    
    main_dish = None
    side_dish = None
    keep = None

    
    def __init__(self, dish_data) -> None:
        self.meal_date = dish_data["meal_date"]
        self.main_dish = dish_data["main_dish"]
        self.side_dish = dish_data["side_dish"]
        self.keep = dish_data.get("keep", "0")  # Default to "0" (not kept) for backward compatibility
    
    # Meal
    @staticmethod
    def check_db_existing():
        exists = Pylavor.check_file_exists(f"data/{Meal.database_name}")
        
        if not exists:
            Pylavor.create_folder("data")
            Pylavor.json_write("data", Meal.database_name, {}, sanitation=False)
            
    
    # Meal
    def save(self):
        all_meals = Pylavor.json_read("data", Meal.database_name)

        all_meals[str(self.meal_date)] = self.to_json()
        
        Pylavor.json_write("data", Meal.database_name, all_meals)    
    
    
    # Meal
    @staticmethod
    def get_one(meal_date):
        meal_date = str(meal_date)
        all_meals = Pylavor.json_read("data", Meal.database_name)

        if meal_date not in all_meals:
            return False

        return all_meals[meal_date]

    # Meal
    @staticmethod
    def get_all(type_="all", limit=0):
        Meal.check_db_existing()
     
        all_meals = Pylavor.json_read("data", Meal.database_name)
        
        if type_ != "all":
            if type_.startswith("not_"):
                type_ = type_[4:]
                all_meals = {k: v for k, v in all_meals.items() if v["type_"] != type_}
            else:
                all_meals = {k: v for k, v in all_meals.items() if v["type_"] == type_}
        
        sorted_meals = dict(sorted(all_meals.items(), key=lambda item: item[1]["meal_date"], reverse=True))
            
        if limit != 0:
            return dict(itertools.islice(sorted_meals.items(), limit))
        else:
            return sorted_meals
    
    
    # Meal
    @staticmethod
    def get_week_dates(week_offset=0):
        """
        Returns list of dates (yyyy-mm-dd) for the week starting on Monday,
        with a given offset from the current week.
    
        week_offset = 0 → this week
        week_offset = 1 → next week
        week_offset = -1 → last week
        """
        today = date.today()
        # Find the Monday of this week
        start_of_week = today - timedelta(days=today.weekday())
        # Offset by number of weeks
        target_monday = start_of_week + timedelta(weeks=week_offset)
    
        # Generate dates from Monday to Sunday
        return [(target_monday + timedelta(days=i)).isoformat() for i in range(7)]        
    
    # Meal
    def randomize(self):
        # Check if there's a special food for this day of week
        special_food = DaySpecialFood.get_for_date(self.meal_date)
        
        if special_food and special_food.get("main_dish"):
            # Use special food for this day
            self.main_dish = special_food["main_dish"]
            self.side_dish = special_food.get("side_dish", "")
            self.save()
            return
        
        # No special food, randomize normally
        all_main_dishes = [id_ for id_, _ in Dish.get_all(type_="1", planner_calc=True).items()]
        all_side_dishes = [id_ for id_, _ in Dish.get_all(type_="0", planner_calc=True).items()]        
        
        index = random.randrange(0, len(all_main_dishes))
        popped_item = all_main_dishes.pop(index)
        main_dish = popped_item
        
        dish_data = Dish.get_one(main_dish)
        
        if dish_data["need_sidedish"] == "1":
            # side dish
            if len(all_side_dishes) == 0:
                all_side_dishes = [id_ for id_, _ in Dish.get_all(type_="0", planner_calc=True).items()]   
            if len(all_side_dishes) != 0:
                index = random.randrange(0, len(all_side_dishes))
                popped_item = all_side_dishes.pop(index)
                side_dish = popped_item
            else:
                side_dish = ""
                
        else:
            side_dish = ""        

        
        self.main_dish = main_dish
        self.side_dish = side_dish    
  
        self.save()
        
    
    # Meal
    @staticmethod
    def generate_week(week):
        dates = Meal.get_week_dates(int(week))
        
        all_main_dishes = [id_ for id_, _ in Dish.get_all(type_="1", planner_calc=True).items()]
        all_side_dishes = [id_ for id_, _ in Dish.get_all(type_="0", planner_calc=True).items()]
                
        for date_ in dates:
            # Check if meal exists and is marked as keep
            existing_meal_data = Meal.get_one(date_)
            if existing_meal_data and existing_meal_data.get("keep") == "1":
                # Skip this day, keep the existing meal
                continue
            
            # Check if there's a special food for this day of week
            special_food = DaySpecialFood.get_for_date(date_)
            
            if special_food and special_food.get("main_dish"):
                # Use special food for this day
                main_dish = special_food["main_dish"]
                side_dish = special_food.get("side_dish", "")
            else:
                # No special food, randomize normally
                # main dish
                if len(all_main_dishes) == 0:
                    all_main_dishes = [id_ for id_, _ in Dish.get_all(type_="1", planner_calc=True).items()]
                index = random.randrange(0, len(all_main_dishes))
                
                popped_item = all_main_dishes.pop(index)
                main_dish = popped_item
                
                dish_data = Dish.get_one(main_dish)
                if dish_data["need_sidedish"] == "1":
                    # side dish
                    if len(all_side_dishes) == 0:
                        all_side_dishes = [id_ for id_, _ in Dish.get_all(type_="0", planner_calc=True).items()]   
                    if len(all_side_dishes) != 0:
                        index = random.randrange(0, len(all_side_dishes))
                        popped_item = all_side_dishes.pop(index)
                        side_dish = popped_item
                    else:
                        side_dish = ""
                        
                else:
                    side_dish = ""
            
            # Preserve keep status if meal already exists
            keep_status = "0"
            if existing_meal_data:
                keep_status = existing_meal_data.get("keep", "0")
            
            meal_data = {"meal_date": date_,
                "main_dish": main_dish,
                "side_dish": side_dish,
                "keep": keep_status
                }
            meal = Meal(meal_data)
            meal.save()
        
    
    # Meal
    def to_json(self):
        data_ = {"meal_date": self.meal_date,
                 "main_dish": self.main_dish,
                 "side_dish": self.side_dish,
                 "keep": self.keep
            }

        return data_
    
    
    # Meal
    @staticmethod
    def yes_no(yes_no):
        if yes_no == 1 or yes_no == "1" or yes_no == True:
            return "Da"
        else:
            return "Ne"
        