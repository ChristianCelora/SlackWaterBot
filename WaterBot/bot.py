from datetime import datetime, timedelta, time, date
import pymongo

class User:
    GLASS_PER_LITER = 4
    def __init__(self, user_id: str, water: int, start: time, end: time):
        self.id = user_id
        self.start = start
        self.end = end
        self.water = water
        self.last_drink = datetime.now()
        self.next_drink = datetime.now()
        self.setDailyWater(water)

    def deltaTime(self) -> int:
        h1, m1 = self.start.hour, self.start.minute
        h2, m2 = self.end.hour, self.end.minute
        return (h2*60 + m2) - (h1*60 + m1)

    def __updateNextDrinkTime(self) -> datetime:
        time_before_drink = int(self.deltaTime() / self.glass)
        new_time = self.last_drink + timedelta(minutes=time_before_drink)
        if new_time > datetime.combine(date.today(), self.end):
            new_time = datetime.combine(date.today(), self.start) + timedelta(days=1)

        self.next_drink = new_time
    
    def setTimeFrame(self, start: time, end: time):
        self.start = start
        self.end = end
        self.__updateNextDrinkTime() # Updates next drink

    def setDailyWater(self, water: int):
        self.water = water
        self.glass = int(water * self.GLASS_PER_LITER)
        self.__updateNextDrinkTime() # Updates next drink

    def drink(self):
        self.last_drink = datetime.now()
        self.__updateNextDrinkTime() # Updates next drink

    def getDataAsDict(self, time_format="%H:%M:%S") -> dict:
        return {
            "user_id": self.id,
            "water": self.water,
            "start": self.start.strftime(time_format),
            "end": self.end.strftime(time_format)
        }

class WaterBot:
    DEFAULT_USER_WATER = 2
    DEFAULT_USER_TIME = [time(8,0,0), time(18,0,0)] # start 08:00, end 18:00
    TIME_FORMAT = "%H:%M:%S"
    
    def __init__(self, db: pymongo.database.Database):
        self.users = {}
        self.collection = db.subscriber

    def update(self) -> list:
        notify = []
        #print("notify users")
        for user_id in self.users:
            if self.users[user_id].next_drink < datetime.now():
                notify.append(self.users[user_id])
                self.users[user_id].drink()
            #print(user_id, "next drink", self.users[user_id].next_drink)
        return notify
    
    def addUser(self, user_id: str, water=2, start=time(8,0,0), end=time(18,0,0)) -> str:
        if user_id in self.users:
            return -1  
        user = User(user_id, water, start, end)
        self.users[user_id] = user
        self.collection.replace_one({"user_id": user_id}, user.getDataAsDict(self.TIME_FORMAT), True)
        return user_id

    def removeUser(self, user_id: str) -> str:
        if user_id in self.users:
            removed_user = self.users.pop(user_id)
            self.collection.delete_one({"user_id": removed_user.id})
            return user_id
        return -1

    def setUserWater(self, user_id: str, water: int):
        if user_id not in self.users:
            raise KeyError("User not subscribed")
        self.users[user_id].setDailyWater(int(water))
        self.collection.update_one({"user_id":user_id},{"$set":{"water": int(water)}})

    def setUserTime(self, user_id: str, start: str, end: str):
        if user_id not in self.users:
            raise KeyError("User not subscribed")
        # Will raise ValueError on invalid inputs
        h1,m1 = [ int(x) for x in start.split(":")]
        h2,m2 = [ int(x) for x in end.split(":")]
        if time(h1,m1,0) >= time(h2,m2,0):
            raise ValueError("End time cannot be earlier than start")
        self.users[user_id].setTimeFrame(time(h1,m1,0), time(h2,m2,0))
        self.collection.update_one(
            {"user_id":user_id}, 
            {"$set":{
                "start": time(h1,m1,0).strftime(self.TIME_FORMAT), 
                "end": time(h2,m2,0).strftime(self.TIME_FORMAT)
            }}
        )

    def getUser(self, user_id: str) -> User:
        if user_id not in self.users:
            raise KeyError("User not subscribed")
        return self.users[user_id]
