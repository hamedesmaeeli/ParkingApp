# test_method_exists.py
from database import ParkingDatabase

db = ParkingDatabase()
print(dir(db))  # لیست همه متدها را نشان می‌دهد
if hasattr(db, 'get_card_by_uid'):
    print("✅ متد get_card_by_uid وجود دارد.")
else:
    print("❌ متد get_card_by_uid وجود ندارد.")