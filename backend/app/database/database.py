#so basically sqlalchemy is a library that alllows us to interact with databases in a more pythonic way.
#automatically generates sql queries for us. It follows ORM ie. Object Relational Mapping. 


import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base  #session maker creates a session for us which helps us to interact with the db. 
                                                        #declarative base is a base class for our models. It helps us to create tables in the db.


DATABASE_URL = os.getenv(      #tells us where the database is located and how to connect to it. It contains the username, password, host, port and database name.
    "DATABASE_URL", "postgresql://schema_user:schema_password@localhost:5433/schema_drift_db"
)


engine = create_engine( #used for communication with postgres database. 
    DATABASE_URL        #when engine is created, connection pool is also created. 
)


SessionLocal = sessionmaker(   #this creates sessions. autocommit is set to false coz we dont want it to commit automatically.
    autocommit=False,          #it will only save changes when we call commit explicitly.
    autoflush=False,
    bind=engine
)


Base = declarative_base()     #base is basically like a badge. it helps python understand which classes are database models and which are not. 
#it basically helps a class become a base where sqlalchemy models can inherit from. 