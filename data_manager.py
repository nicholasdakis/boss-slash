import json, os

class DataManager:
    def __init__(self,filename="user_data.json"):
        self.filename=filename
        self.data={
            "coins": 0,
            "fire_rate":0,
            "damage":0,
            "vitality":0,
            "speed":0
        }
        self.load()

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)

    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                self.data = json.load(f)
        else: # if the file doesn't exist, "save" a default file
            self.save()

    def store_coins(self,amount):
        self.data["coins"]=amount
        self.save()

    def store_upgrade(self,upgrade_name,level):
        self.data[upgrade_name]=level
        self.save()