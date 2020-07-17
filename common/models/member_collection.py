# coding: utf-8
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy


from config.DB import db


class MemberCollection(db.Model):
    __tablename__ = 'member_collection'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    commodity_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
