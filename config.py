class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:root@localhost:3306/service_shop_db'
    DEBUG = True
    
class TestingConfig:
    pass

class ProductionConfig:
    pass