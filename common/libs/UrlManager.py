# -*- coding: utf-8 -*-
from flask import Flask
app=Flask(__name__)
import time
from config.base_setting import APP,UPLOAD
class UrlManager(object):
    def __init__(self):
        pass

    @staticmethod
    def buildUrl( path ):
        return path

    @staticmethod
    def buildStaticUrl(path):
        # release_version = app.config.get( "release_version" )
        ver = "%s"%( "first" )
        path =  "/static" + path + "?ver=" + ver
        return UrlManager.buildUrl( path )

    @staticmethod
    def buildImageUrl(path):
        config1 = APP
        config2 = UPLOAD
        url = config1['domain'] + config2['prefix_url'] + path
        return url