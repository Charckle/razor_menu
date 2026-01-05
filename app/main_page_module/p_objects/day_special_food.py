from app.pylavor import Pylavor
from datetime import datetime


class DaySpecialFood:
    database_name = "day_special_foods_db.json"
    
    # Day of week: 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday
    day_of_week = None
    main_dish = None
    side_dish = None
    
    def __init__(self, data) -> None:
        self.day_of_week = data["day_of_week"]
        self.main_dish = data.get("main_dish", "")
        self.side_dish = data.get("side_dish", "")
    
    @staticmethod
    def check_db_existing():
        exists = Pylavor.check_file_exists(f"data/{DaySpecialFood.database_name}")
        
        if not exists:
            Pylavor.create_folder("data")
            Pylavor.json_write("data", DaySpecialFood.database_name, {}, sanitation=False)
    
    def save(self):
        all_special_foods = Pylavor.json_read("data", DaySpecialFood.database_name)
        
        all_special_foods[str(self.day_of_week)] = self.to_json()
        
        Pylavor.json_write("data", DaySpecialFood.database_name, all_special_foods)
    
    @staticmethod
    def get_one(day_of_week):
        DaySpecialFood.check_db_existing()
        day_of_week = str(day_of_week)
        all_special_foods = Pylavor.json_read("data", DaySpecialFood.database_name)
        
        if day_of_week not in all_special_foods:
            return False
        
        return all_special_foods[day_of_week]
    
    @staticmethod
    def get_all():
        DaySpecialFood.check_db_existing()
        all_special_foods = Pylavor.json_read("data", DaySpecialFood.database_name)
        return all_special_foods
    
    @staticmethod
    def get_for_date(date_string):
        """
        Get special food for a specific date.
        date_string should be in format "YYYY-MM-DD"
        Returns False if no special food is set for that day of week.
        """
        date_obj = datetime.strptime(date_string, "%Y-%m-%d")
        day_of_week = date_obj.weekday()  # Monday=0, Sunday=6
        
        return DaySpecialFood.get_one(day_of_week)
    
    @staticmethod
    def delete(day_of_week):
        all_special_foods = Pylavor.json_read("data", DaySpecialFood.database_name)
        
        if str(day_of_week) in all_special_foods:
            del all_special_foods[str(day_of_week)]
            Pylavor.json_write("data", DaySpecialFood.database_name, all_special_foods)
            return True
        return False
    
    def to_json(self):
        data_ = {
            "day_of_week": self.day_of_week,
            "main_dish": self.main_dish,
            "side_dish": self.side_dish
        }
        return data_
    
    @staticmethod
    def get_day_name(day_of_week):
        """Get the name of the day in Slovenian"""
        days = {
            0: "Ponedeljek",
            1: "Torek",
            2: "Sreda",
            3: "Četrtek",
            4: "Petek",
            5: "Sobota",
            6: "Nedelja"
        }
        return days.get(day_of_week, "")

