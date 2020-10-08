from sqlalchemy import (
    create_engine, 
    Sequence,Column, 
    String, 
    Integer, 
    ForeignKey, 
    Table,
    DateTime
)

from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):

    __tablename__ = 'users'

    id = Column(Integer, Sequence('user_id_sequence'), primary_key=True)
    
    username = Column(String(50))

    password = Column(String(50))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'{self.username}'

class Classification(Base):

    __tablename__ = 'classifications'

    id = Column(Integer, Sequence('classifications_id_sequence'), primary_key=True)

    name = Column(String(50), index=True)

    products = relationship('Product', back_populates='classification', lazy='dynamic')

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return self.name


class ColorSize(Base):

    __tablename__ = 'color_size'

    color_id = Column(Integer, ForeignKey('products_colors.id'), primary_key=True)
    product_size_id = Column(Integer, ForeignKey('products_sizes.id'), primary_key=True)

    color = relationship('ProductColor', back_populates='color_sizes')
    size = relationship('ProductSize', back_populates='size_colors')

    repeating_counter = Column(Integer, default=1)

class ProductSize(Base):

    __tablename__ = 'products_sizes'

    id = Column(Integer, Sequence('products_colors_sequence'), primary_key=True)
    size = Column(Integer, index=True)

    size_colors = relationship('ColorSize', back_populates='size')

    def __repr__(self):
        return f'{self.size}'

class ProductColor(Base):

    __tablename__ = 'products_colors'

    id = Column(Integer, Sequence('products_colors_sequence'), primary_key=True)

    name = Column(String(50))

    product_id = Column(Integer, ForeignKey('products.id'))
    product = relationship('Product', back_populates='colors')

    color_sizes = relationship('ColorSize', back_populates='color', cascade='all, delete')

    def __repr__(self):
        return self.name

class Product(Base):

    __tablename__ = 'products'

    id = Column(Integer, Sequence('product_id_sequence'), primary_key=True)

    sku_code = Column(String(50), index=True)

    pairs_number = Column(Integer)

    image = Column(String(50))

    original_price = Column(Integer)
    suggested_price = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    classification_id = Column(Integer, ForeignKey('classifications.id'))
    classification = relationship('Classification', back_populates='products')

    colors = relationship('ProductColor', back_populates='product', cascade="all, delete")

    sold_units = relationship('SoldProduct', back_populates='product')


    def __repr__(self):

        return self.sku_code


class SoldProduct(Base):

    __tablename__ = 'sold_products'

    id = Column(Integer, Sequence('sold_products_sequence'), primary_key=True)

    product_id = Column(Integer, ForeignKey('products.id'))
    product = relationship('Product', back_populates='sold_units')

    color = Column(String)
    size = Column(Integer)

    sold_by_price = Column(Integer)

    sold_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'{self.product.sku_code} sold_unit'

engine = create_engine('sqlite:///shop.db')


def get_db_session():
    # make sure all tables created
    Base.metadata.create_all(engine)

    # creating session 
    Session = sessionmaker(bind=engine)
    session = Session()

    return session

def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance




