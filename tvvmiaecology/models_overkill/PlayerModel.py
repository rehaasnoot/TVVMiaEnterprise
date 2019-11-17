from .__init__ import *

class PlayerModel(TVVBase, TVVModelAux):
    __tablename__ = 'tvvplayer'
    id = Column('id', Integer, primary_key=True, nullable=False, autoincrement=True)
    uuid = Column('uuid', String, nullable=False, default=newUUID(__tablename__))
    name = Column('name', String, nullable=False)
    description = Column('description', String, nullable=False)
    uri = Column('uri', String, nullable=False)
    #players = relationship('OrderModel', backref='player')
#    orders = relationship('OrderModel', back_populates='player')
