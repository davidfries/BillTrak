import records
from secrets import secrets as secrets



class LoggingBackend():
    try:
        db = records.Database(
            f"postgresql://192.168.5.172/billtrak?user=dj&password={secrets.dbpw}")
    except Exception as e:
        print("error in db connection {}".format(e))
    def logevent(self,event):
        query="""insert into logs(event) values(:event)
        """
        try:
            self.db.query(query,event=str(event))
        except Exception as e:
            print(e) 