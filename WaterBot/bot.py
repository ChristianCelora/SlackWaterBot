from datetime import datetime, timedelta

class WaterBot:
    def __init__(self):
        self.users = {}

    def update(self) -> list:
        notify = []
        print("notify users")
        for user_id in self.users:
            if self.users[user_id].next_glass < datetime.now():
                print(self.users[user_id].id, "need a drink!")
                notify.append(self.users[user_id])
                self.users[user_id].updateNextDrinkTime()
            print("user", self.users[user_id].id, "next drink", self.users[user_id].next_glass)
        return notify

    def addUser(self, user_id: str) -> str:
        if user_id not in self.users:
            self.users[user_id] = User(user_id, 8, "8:00", "18:00")
            return "User subscribed"
        return "User alredy subscribed"

    def removeUser(self, user_id: str) -> str:
        if user_id in self.users:
            self.users.pop(user_id)
        return "User unsubscribed"

    def setUserWater(self, user_id: str, water: int):
        if user_id not in self.users:
            raise KeyError()
        self.users[user_id].setDailyWater(water)
        
        

class User:
    GLASS_PER_LITER = 4
    def __init__(self, user_id: str, water: int, start: str, end: str):
        self.id = user_id
        self.start = start
        self.end = end
        self.last_drink = datetime.now()
        self.next_glass = datetime.now()
        self.setDailyWater(water)

    def deltaTime(self) -> int:
        h1, m1 = self.start.split(":")
        h2, m2 = self.end.split(":")
        return (int(h2)*60 + int(m2)) - (int(h1)*60 + int(m1))

    def updateNextDrinkTime(self) -> datetime:
        time_before_drink = int(self.deltaTime() / self.glass)
        memo = self.next_glass
        self.next_glass = self.last_drink + timedelta(minutes = time_before_drink)
        self.last_drink = memo
        print("last_drink", self.last_drink)
    
    def setDailyWater(self, water: int):
        self.glass = water * self.GLASS_PER_LITER
        self.updateNextDrinkTime() # Updates next drink
