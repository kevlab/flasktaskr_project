from project import db
#from project.models import Task, User
#from datetime import date

# create the db and the db table
db.create_all()

# insert dummy data
#db.session.add(User("admin", "admin@gmail.com", "admin", "admin"))
#
#db.session.add(Task("Finish this tutorial", date(2015, 3, 13), 10,
               #date(2015, 2, 13), 1, 1))
#db.session.add(Task("Finish Real Python", date(2015, 3, 13), 10,
               #date(2015, 1, 13), 1, 1))

# commit changes
db.session.commit()
