from sqlalchemy import Column, Integer, String, Sequence, ForeignKey, Date, Table, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

has_sub = Table('has_sub', Base.metadata,
                Column('user_id', String, ForeignKey('user.id')),
                Column('series_id', Integer, ForeignKey('series.id'))
               )


owns_comic = Table('owns_comic', Base.metadata,
                Column('user_id', String, ForeignKey('user.id')),
                Column('comic_id', Integer, ForeignKey('comics.id'))
               )

# Entities
class User(Base):
    __tablename__ = 'user'
    id = Column(String, primary_key=True)
    name = Column(String)

    series_child = relationship("Series", secondary=has_sub, back_populates='user_child')
    comic_child = relationship('Comics', secondary=owns_comic, back_populates='user_child')


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
    release_date = Column(Date)
    image_link = Column(String)
    seriesID = Column(Integer, ForeignKey('series.id'))

    user_child = relationship('User', secondary=owns_comic, back_populates='comic_child')

    def get(self):
        return (self.id,
                self.title,
                self.release_date,
                self.url,
                self.release_date < datetime.date(datetime.now()),
                self.seriesID)

