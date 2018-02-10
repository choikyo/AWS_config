from sqlalchemy import Column, ForeignKey, Integer, String, Date, Numeric, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy import func

Base = declarative_base()

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    description = Column(String(500), nullable = False)
    insert_date = Column(DateTime(timezone=True), server_default = func.now(), nullable = False)
    
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id':self.id,
            'name':self.name,
            'description': self.description
        }
        

class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(500), nullable = False)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    insert_date = Column(DateTime(timezone=True), server_default = func.now(), nullable = False)
    created_by = Column(String(250), nullable=False)
    
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id':self.id,
            'name':self.name,
            'description': self.description
        }

engine = create_engine('postgresql://catalog:password@localhost/catalog')


Base.metadata.create_all(engine)
