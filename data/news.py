import datetime# Подключаем модуль для работы с датой и временем.
import sqlalchemy #Это библиотека SQLAlchemy — она нужна, чтобы работать с базой данных через Python (ORM).
from sqlalchemy import orm#Импортируем часть SQLAlchemy для работы со связями между таблицами.
from .db_session import SqlAlchemyBase#это "основа" для всех моделей базы данных.
from sqlalchemy_serializer import SerializerMixin


class News(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'news'#Указываем имя таблицы в базе данных

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=False)


    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    is_published = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    user = orm.relationship('User', back_populates='news')
    def __repr__(self):

        return f'<запись> {self.id} {self.title} {self.content}'


