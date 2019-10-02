from sqlalchemy import Column, DateTime, Integer, String, TEXT, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    creation_date = Column(DateTime(timezone=True), server_default=func.now())
    update_date = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        fields = ""
        for c in self.__table__.columns:
            if fields == "":
                fields = "{}='{}'".format(c.name, getattr(self, c.name))
            else:
                fields = "{}, {}='{}'".format(fields, c.name, getattr(self, c.name))
        return "<{}({})>".format(self.__class__.__name__, fields)

    @staticmethod
    def list_as_dict(items):
        return [i.as_dict() for i in items]

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Order(BaseModel):
    STATUS_CREATED = "Created"
    STATUS_FINISHED = "Finished"

    __tablename__ = "manufacturing_order"
    id = Column(Integer, primary_key=True)
    number_of_pieces = Column(Integer, nullable=False)
    description = Column(TEXT, nullable=False, default="No description")
    status = Column(String(256), nullable=False, default="Created")

    pieces = relationship("Piece", lazy="joined")

    def as_dict(self):
        d = super().as_dict()
        d['pieces'] = [i.as_dict() for i in self.pieces]
        return d


class Piece(BaseModel):
    STATUS_CREATED = "Created"
    STATUS_CANCELLED = "Cancelled"
    STATUS_QUEUED = "Queued"
    STATUS_MANUFACTURING = "Manufacturing"
    STATUS_MANUFACTURED = "Manufactured"

    __tablename__ = "piece"
    ref = Column(Integer, primary_key=True)
    manufacturing_date = Column(DateTime(timezone=True), server_default=None)
    status = Column(String(256), default=STATUS_QUEUED)
    order_id = Column(Integer, ForeignKey('manufacturing_order.id'))
    order = relationship('Order', backref='piece')
