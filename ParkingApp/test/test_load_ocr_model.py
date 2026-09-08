
from hezar.models import Model

# بارگذاری مدل از هاب
model = Model.load("hezarai/crnn-fa-license-plate-recognition-v2")

# ذخیره مدل به صورت محلی (برای استفاده آفلاین)
model.save("my-license-plate-ocr")