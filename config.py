# إعدادات الاتصال بقاعدة بيانات MongoDB
import os

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'cadoz')
COLLECTION_NAME = os.environ.get('COLLECTION_NAME', 'products')
