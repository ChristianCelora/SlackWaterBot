import pytest
from WaterBot.bot import WaterBot, User
from freezegun import freeze_time
from datetime import datetime, timedelta, time, date
import json

# INIT
bot = WaterBot()
# mock datetime.now()
NOW = datetime.now()
"""FAKE_TIME = datetime.datetime(NOW.year, NOW.month, NOW.day, 14, 0, 0)
@pytest.fixture
def mock_datetime_now(monkeypatch):
    class mydatetime:
        @classmethod
        def now(cls):
            return FAKE_TIME
    monkeypatch.setattr(datetime, 'datetime', mydatetime)

def test_patch_datetime(mock_datetime_now):
    assert datetime.datetime.now() == FAKE_TIME"""

# TESTS
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
    user = User(user_id, 8, time(8,0,0), time(18,0,0))
    assert user.deltaTime() == 600
    user = User(user_id, 8, time(8,0,0), time(8,30,0))
    assert user.deltaTime() == 30

@freeze_time(datetime.today().strftime("%Y-%m-%d")+" 14:00:00")
def test_set_next_drink_time_on_user_init():
    user = User("TEST", 2, time(8,0,0), time(18,0,0))
    first_drink = user.next_drink
    expect_date = datetime.now() + timedelta(minutes = int(600/8))
    assert user.next_drink.date() == expect_date.date()                 # date
    assert user.next_drink.strftime("%H") == expect_date.strftime("%H") # hour
    assert user.next_drink.strftime("%M") == expect_date.strftime("%M") # minute

def test_update_users():
    res = bot.addUser("TEST4")
    users = bot.update()
    assert type(users) == list

def test_set_init_user_water():
    res = bot.setUserWater("TEST4", 4)
    user = bot.users["TEST4"]
    assert bot.users["TEST4"].glass == 16

def test_set_init_user_water_with_string():
    res = bot.setUserWater("TEST4", "20")
    assert bot.users["TEST4"].glass == 80

def test_user_drink():
    user = User("TEST", 2, time(8,0,0), time(18,0,0))
    now = datetime.now()
    user.drink()
    assert user.last_drink < user.next_drink
    assert user.last_drink.date() == now.date()                 # date
    assert user.last_drink.strftime("%H") == now.strftime("%H") # hour
    assert user.last_drink.strftime("%M") == now.strftime("%M") # minute 

def test_exception_set_user_water():
    with pytest.raises(KeyError):
        bot.setUserWater("NOT_FOUND", 4)

@freeze_time(datetime.today().strftime("%Y-%m-%d")+" 14:00:00")
def test_update_user_water():
    liters = 4
    user = User("TEST", liters, time(8,0,0), time(18,0,0))
    actual_date = user.next_drink
    expect_date = datetime.now() + timedelta(minutes = int(600/(liters*4)))
    assert actual_date.date() == expect_date.date()                 # date
    assert actual_date.strftime("%H") == expect_date.strftime("%H") # hour
    assert actual_date.strftime("%M") == expect_date.strftime("%M") # minute

def test_update_user_water_high_value():
    liters = 20
    user = User("TEST", liters, time(8,0,0), time(18,0,0))
    assert user.water == liters
    assert user.glass == 20*4
    
def test_refactoring_user_timeframe():
    user = User("TEST", 2, time(8,1,0), time(18,2,0))
    assert user.start == time(8, 1 ,0)
    assert user.end == time(18, 2, 0)

@freeze_time(datetime.today().strftime("%Y-%m-%d")+" 14:00:00")
def test_set_user_timeframe():
    bot.addUser("TEST6")
    user = bot.users["TEST6"]
    expect_time = user.last_drink + timedelta(minutes = int(540/(2*4)))
    bot.setUserTime("TEST6", "9:45", "18:45")
    assert user.start == time(9, 45 ,0)
    assert user.end == time(18, 45, 0)
    actual_time = user.next_drink
    assert actual_time.hour == expect_time.hour # hour
    assert actual_time.minute == expect_time.minute # minute

def test_exception_set_user_timeframe():
    with pytest.raises(KeyError):
        bot.setUserTime("NOT_FOUND", "9:45", "18:45")

def test_exception_refactoring_user_timeframe():
    bot.addUser("TEST7")
    with pytest.raises(ValueError):
        bot.setUserTime("TEST7", "aa", "18:45")
    with pytest.raises(ValueError):
        bot.setUserTime("TEST7", "9:45", "bb")
    with pytest.raises(ValueError):
        bot.setUserTime("TEST7", "18:02", "8:01")
    with pytest.raises(ValueError):
        bot.setUserTime("TEST7", "aa:02", "8:bb")

def test_get_user_info():
    bot.addUser("TEST8")
    user_data = bot.getUser("TEST8")
    assert user_data == bot.users["TEST8"]

def test_get_user_not_found_info():
    with pytest.raises(KeyError):
        bot.getUser("NOT_FOUND")

def test_update_user_after_end_time():
    initial_datetime = datetime.combine(date.today(), time(20,0,0))
    next_datetime = datetime.combine(date.today(), time(22,00,0))
    with freeze_time(initial_datetime) as frozen_datetime: # manual ticks
        assert frozen_datetime() == initial_datetime # test freezing
        bot.addUser("TEST9")
        bot.setUserTime("TEST9", "9:45", "18:45")
        bot.users["TEST9"].next_drink = datetime.now() - timedelta(seconds=5)
        bot.addUser("TEST10")
        bot.setUserTime("TEST10", "9:45", "22:45")
        bot.users["TEST10"].next_drink = datetime.now() - timedelta(seconds=5)
        notify_users = bot.update()
        frozen_datetime.move_to(next_datetime)
        notify_users = bot.update()
        assert bot.users["TEST9"] not in notify_users
        assert bot.users["TEST10"] in notify_users

def test_get_user_data_as_json():
    user = User("TEST", 2, time(8,0,0), time(18,0,0))
    expected_json = {
        "user_id": "TEST",
        "water": 2,
        "start": "08:00:00",
        "end": "18:00:00"
    }
    actual_json = user.getJson()
    assert json.dumps(expected_json) == actual_json
