from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

dispatch_table = Table('dispatch_table', Base.metadata,
                       Column('tg_user_id', ForeignKey('__TelegramUser__.id')),
                       Column('subsciprion_id', ForeignKey('__Subscription__.id')),
                      )


class TelegramUser(Base):
    __tablename__ = '__TelegramUser__'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, nullable=False, unique=True)
    subs = relationship('Subscription', secondary=dispatch_table, back_populates='users')

    def __str__(self):
        return f'Telegram User id: {self.telegram_id}'


class Service(Base):
    __tablename__ = '__Service__'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)


class Subscription(Base):
    __tablename__ = '__Subscription__'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    service = Column(Integer, ForeignKey('__Service__.id'))
    subscription_token = Column(String, nullable=False) # id, services, url, group_id etc to access with service's api

    users = relationship('TelegramUser', secondary=dispatch_table, back_populates='subs')

    def __str__(self):
        return f'Subscription: {self.name}'


