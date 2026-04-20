from flask import Flask, url_for, abort
from flask import request
from forms.user import RegisterForm
from flask  import render_template
from loginform import LoginForm
from flask import redirect
from data import  db_session
from data.departments import Department
from data.Jobs import Jobs
from data.users import User
from data.news import News
from data.departments import Department
from forms.user import RegisterForm
from flask import make_response
from flask_login import LoginManager
from flask_login import login_user
from flask_login import login_user, current_user, login_required
from forms.news import NewsForm
from forms.departments import DepartmentsForm
from data import db_session, news_api, user_api, city_from_api
from sqlalchemy_serializer import SerializerMixin
from flask import jsonify
from flask_restful import reqparse, abort, Api, Resource
from flask import jsonify



parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('is_private', required=True, type=bool)
parser.add_argument('user_id', required=True, type=int)

def abort_if_news_not_found(news_id):
    session = db_session.create_session()
    news = session.query(News).get(news_id)
    if not news:
        abort(404, message=f"News {news_id} not found")

class NewsResource(Resource):
    def get(self, news_id):
        abort_if_news_not_found(news_id)
        session = db_session.create_session()
        news = session.get(News, news_id)
        return jsonify({'news': news.to_dict(
            only=('title', 'content', 'user_id', 'is_private'))})

    def delete(self, news_id):
        abort_if_news_not_found(news_id)
        session = db_session.create_session()
        news = session.get(News, news_id)
        session.delete(news)
        session.commit()
        return jsonify({'success': 'OK'})



class NewsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        news = session.query(News).all()
        return jsonify({'news': [item.to_dict(
            only=('title', 'content', 'user.name')) for item in news]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        news = News(
            title=args['title'],
            content=args['content'],
            user_id=args['user_id'],
            is_private=args['is_private']
        )
        session.add(news)
        session.commit()
        return jsonify({'id': news.id})