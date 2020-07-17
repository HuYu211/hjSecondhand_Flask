# -*- coding: utf-8 -*-
from werkzeug.utils import secure_filename
from config.DB import db
from common.libs.helper import getCurrentDate
import urllib.request
import datetime
import os,stat,uuid
from common.libs.helper import getCurrentDate
from config.base_setting import UPLOAD
class UploadService():
	@staticmethod
	def uploadByFile( file,id ):
		config_upload = UPLOAD
		resp = { 'code':200,'msg':'操作成功~~','data':{} }
		filename = secure_filename( file.filename )
		ext = filename.rsplit(".",1)[1]
		if ext not in config_upload['ext']:
			resp['code'] = -1
			resp['msg'] = "不允许的扩展类型文件"
			return resp

		root_path = config_upload['prefix_path']
		#不使用getCurrentDate创建目录，为了保证其他写的可以用，这里改掉，服务器上好像对时间不兼容
		file_dir = datetime.datetime.now().strftime("%Y%m%d")
		save_dir = root_path + id + "/" + file_dir
		print(save_dir)
		if not os.path.exists( save_dir ):
			os.makedirs( save_dir )
			os.chmod( save_dir,stat.S_IRWXU | stat.S_IRGRP |  stat.S_IRWXO )

		file_name = str( uuid.uuid4() ).replace("-","") + "." + ext

		file.save( "{0}/{1}".format( save_dir,file_name ) )


		resp['data'] = {
			'file_key':  id + "/" + file_dir + "/" + file_name
		}
		return resp

# class UploadService():
# 	@staticmethod
# 	def uploadByFile(img_url, id):
# 		resp = {'code': 200, 'msg': '操作成功~~', 'data': {}}
# 		file_name = os.path.basename(img_url)
# 		print(file_name)
# 		root_path = UPLOAD['prefix_path']
# 		file_path = root_path + id
# 		if not os.path.exists(file_path):
# 			# 创建路径
# 			os.makedirs(file_path)
# 		# 获得图片后缀
# 		# file_suffix = os.path.splitext(img_url)[1]
# 		# 拼接图片名（包含路径）
# 		filename = '{}{}{}'.format(file_path, os.sep,file_name )
# 		# 下载图片，并保存到文件夹中
# 		urllib.request.urlretrieve(img_url, filename=filename)
# 		resp["url"] = filename
# 		return resp
