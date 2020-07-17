# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy


from config.DB import db


class CommodityInformation(db.Model):
    __tablename__ = 'commodity_information'

    id = db.Column(db.Integer, primary_key=True)
    authorId = db.Column(db.Integer)
    name = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue())
    price = db.Column(db.String(6), nullable=False, server_default=db.FetchedValue())
    image = db.Column(db.String(1000), nullable=False, server_default=db.FetchedValue())
    area_tab = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue())
    summary = db.Column(db.String(10000), nullable=False, server_default=db.FetchedValue())
    tab = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue())
    type = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue())
    contacts = db.Column(db.String(2000), nullable=False, server_default=db.FetchedValue())
    qqnumber = db.Column(db.String(30), nullable=False, server_default=db.FetchedValue())
    phonenumber = db.Column(db.String(30), nullable=False, server_default=db.FetchedValue())
    status = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue())
    view_count = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    release_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    formid = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue())
    last_count = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())