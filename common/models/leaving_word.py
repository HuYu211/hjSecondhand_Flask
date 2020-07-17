# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy


from config.DB import db


class LeavingWord(db.Model):
    __tablename__ = 'leaving_word'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    commidity_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    information = db.Column(db.String(10000), nullable=False, server_default=db.FetchedValue())
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    formid = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue())
    replyid = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())