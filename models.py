from sqlalchemy import Column, Integer, String, Sequence, ForeignKey, Date, Table, Boolean
from sqlalchemy.orm import relationship
from database import Base

has_sub = Table('has_sub', Base.metadata,
                Column('user_id', Integer, ForeignKey('user.id')),
                Column('series_id', Integer, ForeignKey('series.id'))
               )


# Entities
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String)

    series_child = relationship("Series", secondary=has_sub, back_populates='user_child')

class Series(Base):
    __tablename__ = 'series'
    id = Column(Integer, Sequence('series_id_seq'), primary_key=True)
    name = Column(String)

    user_child = relationship('User', secondary=has_sub, back_populates='series_child')
    comic_child = relationship("Comics")

class Comics(Base):
    __tablename__ = 'comics'
    id = Column(Integer, Sequence('comic_id_seq'), primary_key=True)
    title = Column(String)
    url   = Column(String)
    notes = Column(String)
    release_date = Column(Date)
    image_link = Column(String)
    availability = Column(Boolean)
    seriesID = Column(Integer, ForeignKey('series.id'))

    def get(self):
        return (self.id, self.title,
               self.release_date,
               self.url,
               self.notes,
               self.availability,
               self.seriesID)

