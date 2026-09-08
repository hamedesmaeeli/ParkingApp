# test_get_card.py
from database import ParkingDatabase

db = ParkingDatabase()

# تست با یک UID نمونه
uid = "CF4A1D01"
card = db.get_card_by_uid(uid)
print(f"🔍 نتیجه جستجو برای UID {uid}: {card}")