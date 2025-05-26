class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:root@localhost:3306/service_shop_db'
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    DEBUG = True
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300
    
class TestingConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'
    DEBUG = True
    # CACHE_TYPE = 'SimpleCache'
    CACHE_TYPE = "null"
    
class ProductionConfig:
    pass