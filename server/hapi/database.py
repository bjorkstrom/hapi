from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from . import config


def db_url():
    return "mysql+pymysql://%s:%s@%s/%s?charset=utf8" % \
           (config.DB_USERNAME, config.DB_PASSWORD,
            config.DB_HOST, config.DB_NAME)


engine = create_engine(db_url(),
                       # echo=True,
                       convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    Base.metadata.create_all(bind=engine)
