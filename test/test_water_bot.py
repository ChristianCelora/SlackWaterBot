import pytest
from WaterBot.bot import WaterBot
from WaterBot.bot import User
from datetime import datetime, timedelta

#INIT
bot = WaterBot()

def test_subscribe_user():
    bot.addUser("TEST1")
    assert "TEST1" in bot.users
    bot.removeUser("TEST1")
    assert "TEST1" not in bot.users

def test_subscribe_user_response():
    res = bot.addUser("TEST2")
    assert res == "User subscribed"

def test_subscribe_duplicate_user_response():
    res = bot.addUser("TEST3")
    res2 = bot.addUser("TEST3")
    assert res2 == "User alredy subscribed"

def test_user_delta_time():
    user_id = "TEST"
    user = User(user_id, 8, "8:00", "18:00")
    assert user.deltaTime() == 600
    user = User(user_id, 8, "8:00", "8:30")
    assert user.deltaTime() == 30

def test_set_next_drink_time():
    user = User("TEST", 2, "8:00", "18:00")
    first_drink = user.next_glass
    expect_date = datetime.now() + timedelta(minutes = int(600/8))
    assert user.next_glass.date() == expect_date.date()                 # date
    assert user.next_glass.strftime("%H") == expect_date.strftime("%H") # hour
    assert user.next_glass.strftime("%M") == expect_date.strftime("%M") # minute

def test_update_users():
    res = bot.addUser("TEST4")
    bot.update()

def test_set_user_water():
    res = bot.addUser("TEST4")
    res = bot.setUserWater("TEST4", 4)
    assert bot.users["TEST4"].glass == 16

def test_exception_set_user_water():
    with pytest.raises(KeyError):
        bot.setUserWater("NOT_FOUND", 4)

def test_update_user_water():
    res = bot.addUser("TEST5")
    bot.setUserWater("TEST5", 4)
    actual_date = bot.users["TEST5"].next_glass
    expect_date = datetime.now() + timedelta(minutes = int(600/16))
    user = bot.users["TEST5"]
    assert user.next_glass.date() == expect_date.date()                 # date
    assert user.next_glass.strftime("%H") == expect_date.strftime("%H") # hour
    assert user.next_glass.strftime("%M") == expect_date.strftime("%M") # minute
    


