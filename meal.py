"""Classes to structure the data into the required request
"""

class Meal:
    def __init__(self,
                 servicetype_id: int,
                 req_item: dict,
                 current_balance: int,
                 canteen_id: int = 1):
        self.code_qty_map = {}
        self.item_code_map = {}
        self.req_item = req_item
        self.servicetype_id = servicetype_id
        self.canteen_id = canteen_id
        self.num_days = 14
        self.current_balance = current_balance

    def get_request(self):
        self.request = {
            "Canteen_id": str(self.canteen_id),
            "Servicetype_id": str(self.servicetype_id),
            "cb": f"{float(self.current_balance):.2f}",
            "ar": "Y",
            "payable": ["Y"] * (self.num_days * len(self.item_code_map)),
            "advamt": ["Y"] * (self.num_days * len(self.item_code_map)),
            "dt_gt": ["0.00"] * self.num_days,
            "Submit": "Save+Booking",
            "bd[]": [],
        }
        for date, date_items in self.req_item.items():
            date = date.strftime("%Y-%m-%d")
            self.request["bd[]"].append(date)
            self.request[f"Dish_id_{date}[]"] = []
            self.request[f"prev_{date}[]"] = []
            date_items = {self.item_code_map[k]: v for k, v in date_items.items()}
            for i_code in sorted(date_items):
                if date_items[i_code]:
                    try:
                        self.request[f"Dish_id_{date}[]"].append(i_code)
                    except AttributeError:
                        print(self.request[f"Dish_id_{date}[]"])
                        print(self.request)
                        raise
                max_qty = self.code_qty_map[i_code]
                if max_qty > 1 and date_items[i_code] > 0:
                    self.request[f"qty_{i_code}_{date}"] = min(int(date_items[i_code]), max_qty)
                else:
                    self.request[f"qty_{i_code}_{date}"] = int(max_qty)
                self.request[f"prev_{date}[]"].append(max_qty)
            if isinstance(self.request[f"Dish_id_{date}[]"], list) and len(self.request[f"Dish_id_{date}[]"]) == 1:
                self.request[f"Dish_id_{date}[]"] = self.request[f"Dish_id_{date}[]"][0]
        return self.request

class BreakFast(Meal):
    def __init__(self, req_item: dict, current_balance : int, canteen_id: int = 1):
        super(BreakFast, self).__init__(38, req_item, current_balance, canteen_id=canteen_id)
        self.code_qty_map = {
            186: 1,
            187: 2,
            196: 2,
            225: 1,
            226: 1,
            227: 1,
        }
        self.item_code_map = {
            "basic_breakfast": 186,
            "hot_milk": 187,
            "coffee": 196,
            "butter_sachet": 225,
            "boiled_egg": 226,
            "steamed_banana": 227,
        }


class Lunch(Meal):
    def __init__(self, req_item: dict, current_balance : int, canteen_id: int = 1):
        super(Lunch, self).__init__(39, req_item, current_balance, canteen_id=canteen_id)
        self.code_qty_map = {
            188: 1,
            197: 2,
            198: 1,
            231: 1,
            232: 1,
            233: 1,
            236: 1,
            237: 1,
        }
        self.item_code_map = {
            "basic_lunch": 188,
            "appalam": 197,
            "salad": 198,
            "south_indian_dish": 231,
            "dal_of_the_day": 232,
            "dessert": 233,
            "chicken_dish": 236,
            "fish_dish": 237,
        }


class Dinner(Meal):
    def __init__(self, req_item: dict, current_balance : int, canteen_id: int = 1):
        super(Dinner, self).__init__(40, req_item, current_balance, canteen_id=canteen_id)
        self.code_qty_map = {
            189: 1,
            190: 1,
            191: 1,
            192: 1,
            193: 1,
            241: 1,
            242: 1,
            298: 1,
        }
        self.item_code_map = {
            "basic_dinner": 189,
            "fish_fry": 190,
            "veg_special": 191,
            "paneer_dish": 192,
            "non_veg_chicken": 193,
            "salad": 241,
            "south_indian": 242,
            "egg_dish": 298,
        }


class Tea(Meal):
    def __init__(self, req_item: dict, current_balance : int, canteen_id: int = 1):
        super(Tea, self).__init__(41, req_item, current_balance, canteen_id=canteen_id)
        self.code_qty_map = {
            194: 2,
            195: 2,
        }
        self.item_code_map = {
            "tea": 194,
            "snacks": 195,
        }
