from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from envs import envs
Base = declarative_base()

class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    event = Column(String)

class LoggingBackend():
    try:
        engine = create_engine(
            f"postgresql://{envs['dburl']}/billtrak?user=dj&password={envs['dbpw']}")
        Session = sessionmaker(bind=engine)
        session = Session()
        Base.metadata.create_all(engine)
    except Exception as e:
        print("error in db connection {}".format(e))

    def logevent(self, event):
        try:
            log = Log(event=event)
            self.session.add(log)
            self.session.commit()
        except Exception as e:
            print(e)
