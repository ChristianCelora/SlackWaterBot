from datetime import datetime, timedelta, time

class WaterBot:
    def __init__(self):
        self.users = {}

    def update(self) -> list:
        notify = []
        print("notify users")
        for user_id in self.users:
            if self.users[user_id].next_drink < datetime.now():
                notify.append(self.users[user_id])
                self.users[user_id].drink()
        return notify

    def addUser(self, user_id: str) -> str:
        if user_id not in self.users:
            self.users[user_id] = User(user_id, 8, time(8,0,0), time(18,0,0))
            return "User subscribed"
        return "User alredy subscribed"

    def removeUser(self, user_id: str) -> str:
        if user_id in self.users:
            self.users.pop(user_id)
        return "User unsubscribed"

    def setUserWater(self, user_id: str, water: int):
        if user_id not in self.users:
            raise KeyError("User not subscribed")
        self.users[user_id].setDailyWater(water)

    def setUserTime(self, user_id: str, start: str, end: str):
        if user_id not in self.users:
            raise KeyError("User not subscribed")
        # Will raise ValueError on invalid inputs
        h1,m1 = [ int(x) for x in start.split(":")]
        h2,m2 = [ int(x) for x in end.split(":")]
        if time(h1,m1,0) >= time(h2,m2,0):
            raise ValueError("End time cannot be earlier than start")
        self.users[user_id].start = time(h1,m1,0)
        self.users[user_id].end = time(h2,m2,0)
        

class User:
    GLASS_PER_LITER = 4
    def __init__(self, user_id: str, water: int, start: time, end: time):
        self.id = user_id
        self.start = start
        self.end = end
        self.last_drink = datetime.now()
        self.next_drink = datetime.now()
        self.setDailyWater(water)

    def deltaTime(self) -> int:
        h1, m1 = self.start.hour, self.start.minute
        h2, m2 = self.end.hour, self.end.minute
        return (int(h2)*60 + int(m2)) - (int(h1)*60 + int(m1))

    def __updateNextDrinkTime(self) -> datetime:
        time_before_drink = int(self.deltaTime() / self.glass)
        self.next_drink = self.last_drink + timedelta(minutes = time_before_drink)
    
    def setDailyWater(self, water: int):
        self.glass = int(water * self.GLASS_PER_LITER)
        self.__updateNextDrinkTime() # Updates next drink

    def drink(self):
        self.__updateNextDrinkTime() # Updates next drink
        self.last_drink = datetime.now()
