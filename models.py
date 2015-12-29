from sqlalchemy import Column, Integer, String, Sequence, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String)
    children = relationship("Comics")

    def __repr__(self):
        return "<User(name='%s')>" % (self.name)

class Comics(Base):
    __tablename__ = "comics"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    url   = Column(String)
    release_date = Column(Date)

    parent_id = Column(Integer, ForeignKey('users.id'))
