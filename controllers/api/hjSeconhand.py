from flask import request, jsonify, Flask, Blueprint, Flask, g
from sqlalchemy.exc import InvalidRequestError
import re
import emoji
import json,requests
from datetime import datetime
import time
import ast
from common.libs.helper import getCurrentDate
from common.libs.UploadService import UploadService
from common.libs.UrlManager import UrlManager
from common.libs.MemberService import MemberService
from sqlalchemy import  or_
from config.DB import db
from common.models.member import Member
from common.models.commodity_cat import CommodityCat
from common.models.commodity_information import CommodityInformation
from common.models.leaving_word import LeavingWord
from common.models.member_collection import MemberCollection
from common.models.oauth_member_bind import OauthMemberBind
import common.libs.ASSE
from common.libs.QQService import WeChatService
route_api = Blueprint("api_page", __name__)

@route_api.route("/")
def test():
    return "apitest"

@route_api.route("/goods/<tab>", methods=["GET", "POST"])
def index(tab):
    resp = {'code': 200, 'msg': '操作成功~', 'postsList': {}}
    req = request.values
    type = req['type'] if 'type' in req else ''
    page = int(req['p']) if ('p' in req and req['p']) else 1
    offset = (page - 1) * 6
    limit = 6 * page
    postsList = []
    try:
        if tab == 'news':
            Commodity_List = CommodityInformation.query.filter_by(status=1,).order_by(CommodityInformation.updated_time.desc()).all()[ offset:limit ]
        elif tab == 'hots':
            Commodity_List = CommodityInformation.query.filter_by(status=1,).order_by(CommodityInformation.view_count.desc()).all()[ offset:limit ]
        else:
            if type == '全部':
                Commodity_List = CommodityInformation.query.filter_by( status = 1, tab = tab).order_by(CommodityInformation.id.desc()).all()[ offset:limit ]
            else:
                Commodity_List = CommodityInformation.query.filter_by( status = 1, tab = tab,type = type ).order_by(CommodityInformation.id.desc()).all()[ offset:limit ]

        if Commodity_List:
            for item in Commodity_List:
                reply_count = LeavingWord.query.filter_by( commidity_id = item.id ).count()
                author = Member.query.filter_by( id = item.authorId ).first()
                str_list = item.image
                image_list = str_list.split(',')
                imageList = []
                length = len(image_list)
                if length > 3:
                    length = 3
                for i in range(length):
                    image_data = {
                        'id' : i,
                        'type': 'image',
                        'url': image_list[i]
                    }
                    imageList.append(image_data)
                print(imageList)
                time = str(item.created_time)
                tmp_data = {
                    'id':item.id,
                    'title': item.name,
                    'author_id': item.authorId,
                    'price': item.price,
                    'visit_count': item.view_count,
                    'reply_count': reply_count,
                    'type': item.type,
                    'create_at': time,
                    'imageList': imageList,
                    'area_tab': item.area_tab,
                    'tab':item.tab,
                    'author': {
                        'loginname': author.nickname,
                        'avatar_url':author.avatar
                    }
                }
                postsList.append(tmp_data)
        resp['postsList'] = postsList
        db.session.close()

    except InvalidRequestError:
        db.session.rollback()
    resp['has_more'] = 0 if len(postsList) < 6 else 1
    return jsonify(resp)

@route_api.route("/goods", methods=["GET", "POST"])
def goods():
    resp = {'code': 200, 'msg': '操作成功~', 'content': {}}
    req = request.values
    Commodity_id = req['id'] if 'id' in req else ''
    uid = req['uid'] if 'uid' in req else '1'
    if not Commodity_id:
        resp['code'] = -1
        resp['msg'] = "需要Commodity_id"
        return jsonify(resp)
    if not uid:
        resp['code'] = -1
        resp['msg'] = "需要uid"
        return jsonify(resp)
    #查询货物信息
    Commodity_info = CommodityInformation.query.filter_by( status = 1, id = Commodity_id).first()
    if not Commodity_info:
        resp['code'] = -1
        resp['msg'] = "Commodity_info不存在"
        return jsonify(resp)
    #强转时间戳
    time = str(Commodity_info.created_time)

    # 浏览量+1
    try:
        Commodity_info.view_count += 1
        db.session.commit()
    except InvalidRequestError:
        db.session.rollback()
    #统计回复总数
    reply_count = LeavingWord.query.filter_by(commidity_id=Commodity_info.id).count()
    #得到发布者信息
    author = Member.query.filter_by(id=Commodity_info.authorId).first()
    #分割图片字符串
    str_list = Commodity_info.image
    image_list = str_list.split(',')
    imageList = []
    for i in range(len(image_list)):
        image_data = {
            'id': i,
            'type': 'image',
            'url': image_list[i]
        }
        imageList.append(image_data)
    if (uid == -1):
        is_collect = 'false'
    else:
        collect_info = MemberCollection.query.filter_by(commodity_id=Commodity_info.id, member_id=uid).first()
        if not collect_info:
            is_collect = 'false'
        else:
            is_collect = 'true'
    #获取回复信息
    reply_list = LeavingWord.query.filter_by( commidity_id = Commodity_info.id ).all()
    replise = []
    replise2 = []
    #获取openid
    openid_info = OauthMemberBind.query.filter_by(member_id=Commodity_info.authorId).first()
    if openid_info:
        openidx = openid_info.openid
    else:
        openidx = '0'
    if reply_list:
        for item in reply_list:
            if( item.replyid == 0 ):
                reply_time = str(item.created_time)
                author1 = Member.query.filter_by( id=item.member_id ).first()
                reply = LeavingWord.query.filter_by( replyid = item.id ).all()
                openid_info2 = OauthMemberBind.query.filter_by(member_id=item.member_id).first()
                if openid_info2:
                    openidx2 = openid_info2.openid
                else:
                    openidx2 = '0'
                if reply:
                    for n in reply:
                        author2 = Member.query.filter_by(id=n.member_id).first()
                        reply2_time = str(n.created_time)
                        reply2 = {
                            'id': item.id,
                            'author': {
                                'loginname': author2.nickname,
                                'avatar_url': author2.avatar
                            },
                            'content': n.information,
                            'create_at': reply2_time,
                            'reply_id': n.replyid,
                            'is_uped': 'null'
                        }
                        replise2.append(reply2)

                reply_data = {
                    'id': item.id,
                    'author': {
                        'loginname': author1.nickname,
                        'avatar_url': author1.avatar,
                        'openid':openidx2
                    },
                    'reply':replise2,
                    'content':item.information,
                    'create_at':reply_time,
                    'reply_id': item.replyid,
                    'is_uped': 'null'
                }
                replise2 = []
                replise.append(reply_data)
    resp['content'] = {
        'id': Commodity_info.id,
        'title': Commodity_info.name,
        'author_id': Commodity_info.authorId,
        'price': Commodity_info.price,
        'type' : Commodity_info.type,
        'is_collect': is_collect,
        'tab': Commodity_info.tab,
        'visit_count': Commodity_info.view_count,
        'reply_count': reply_count,
        'create_at': time,
        # 'create_at': Commodity_info.created_time,
        'imageList': imageList,
        'describe':Commodity_info.contacts,
        'area_tab': Commodity_info.area_tab,
        'author': {
            'loginname': author.nickname,
            'avatar_url': author.avatar
        },
        'last_count':Commodity_info.last_count,
        'openid':openidx,
        'ph_num': Commodity_info.phonenumber,
        'qq_num': Commodity_info.qqnumber

    }
    resp['content']['replies'] = replise
    return jsonify(resp)

@route_api.route("/goods/member_collection", methods=["GET", "POST"])
def member_collection():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    member_id = req['member_id'] if 'member_id' in req else ''
    commodity_id = req['collecterid'] if 'collecterid' in req else ''
    if not member_id:
        resp['code'] = -1
        resp['msg'] = "需要member_id"
        return jsonify(resp)
    if not commodity_id:
        resp['code'] = -1
        resp['msg'] = "需要commodity_id"
        return jsonify(resp)

    member_info = Member.query.filter_by(id = member_id).first()
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "member_id不存在"
        return jsonify(resp)

    commodity_info = CommodityInformation.query.filter_by(id = commodity_id).first()
    if not commodity_info:
        resp['code'] = -1
        resp['msg'] = "commodity_info不存在"
        return jsonify(resp)
    try:
        collection = MemberCollection()
        collection.member_id = member_id
        collection.commodity_id = commodity_id
        collection.created_time = getCurrentDate()
        collection.updated_time = getCurrentDate()
        db.session.add(collection)
        db.session.commit()
    except InvalidRequestError:
        db.session.rollback()

    return jsonify(resp)

@route_api.route("/goods/leavingWord", methods=["GET", "POST"])
def leavingWord():
    print("回复")
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    member_id = req['member_id'] if 'member_id' in req else ''
    commodity_id = req['commodity_id'] if 'commodity_id' in req else ''
    information = req['content'] if 'content' in req else ''
    reply_id = req['reply_id'] if 'reply_id' in req else ''
    formid = req['formid'] if 'formid' in req else ''

    if not member_id:
        resp['code'] = -1
        resp['msg'] = "需要member_id"
        return jsonify(resp)
    if not commodity_id:
        resp['code'] = -1
        resp['msg'] = "需要commodity_id"
        return jsonify(resp)
    if not information:
        resp['code'] = -1
        resp['msg'] = "留言不能为空"
        return jsonify(resp)
    if not reply_id:
        resp['code'] = -1
        resp['msg'] = "reply_id不能为空"
        return jsonify(resp)
    if not formid:
        resp['code'] = -1
        resp['msg'] = "formid不能为空"
        return jsonify(resp)



    text = emoji.demojize(information)
    result1 = re.sub(':\S+?:', ' ', text)
    member_info = Member.query.filter_by(id=member_id).first()
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "member_id不存在"
        return jsonify(resp)
    reply_count = LeavingWord.query.filter_by(commidity_id=commodity_id).count()
    commodity_info = CommodityInformation.query.filter_by(id=commodity_id).first()
    if not commodity_info:
        resp['code'] = -1
        resp['msg'] = "commodity_info不存在"
        return jsonify(resp)

    memberid = LeavingWord.query.filter_by(id = int(reply_id)).first()
    oauth_bind_info2 = OauthMemberBind.query.filter_by(member_id=commodity_info.authorId).first()
    if memberid:
        oauth_bind_info = OauthMemberBind.query.filter_by(member_id=memberid.member_id).first()
    else:
        oauth_bind_info=''
    formid1 = commodity_info.formid
    if (int(member_id) == int(commodity_info.authorId)):
        if (int(reply_id)==0):
            try:
                leaving_word = LeavingWord()
                goods_info = CommodityInformation.query.filter_by(id=commodity_id).first()
                leaving_word.member_id = member_id
                leaving_word.commidity_id = commodity_id
                leaving_word.information = result1
                leaving_word.replyid = reply_id
                leaving_word.updated_time = getCurrentDate()
                leaving_word.created_time = getCurrentDate()
                leaving_word.formid = formid
                goods_info.last_count = int(reply_count) + 1
                db.session.add(leaving_word)
                db.session.commit()
                #发送qq小程序推送给商品拥有者
                # sendMessage(commodity_id)
            except InvalidRequestError:
                db.session.rollback()
        else:
            try:

                leaving_word = LeavingWord()
                goods_info = CommodityInformation.query.filter_by(id=commodity_id).first()
                leaving_word.member_id = member_id
                leaving_word.commidity_id = commodity_id
                leaving_word.information = result1
                leaving_word.replyid = reply_id
                leaving_word.updated_time = getCurrentDate()
                leaving_word.created_time = getCurrentDate()
                leaving_word.formid = formid
                goods_info.last_count = int(reply_count) + 1
                db.session.add(leaving_word)
                db.session.commit()
                #发送qq小程序推送给商品拥有者
                # sendMessage(commodity_id)
                reply_info = LeavingWord.query.filter_by(id = int(reply_id)).first()
                if reply_info:
                    formid3 = reply_info.formid
                    sendMessage(commodity_id, formid3, information,oauth_bind_info.openid)
                    print("回复成功")
                    print(formid3)
                else:
                    resp['code'] = -1
                    resp['msg'] = "reply_info不存在"
                    return jsonify(resp)
            except InvalidRequestError:
                db.session.rollback()
    else:
        if (int(reply_id) == 0):
            try:
                leaving_word = LeavingWord()
                leaving_word.member_id = member_id
                leaving_word.commidity_id = commodity_id
                leaving_word.information = result1
                leaving_word.replyid = reply_id
                leaving_word.updated_time = getCurrentDate()
                leaving_word.created_time = getCurrentDate()
                leaving_word.formid = formid
                db.session.add(leaving_word)
                db.session.commit()
                sendMessage(commodity_id,formid1,information,oauth_bind_info2.openid)
            except InvalidRequestError:
                db.session.rollback()
        else:
            try:
                leaving_word = LeavingWord()
                leaving_word.member_id = member_id
                leaving_word.commidity_id = commodity_id
                leaving_word.information = result1
                leaving_word.replyid = reply_id
                leaving_word.updated_time = getCurrentDate()
                leaving_word.created_time = getCurrentDate()
                leaving_word.formid = formid
                db.session.add(leaving_word)
                db.session.commit()
                reply_info = LeavingWord.query.filter_by(id=reply_id).first()
                if reply_info:
                    formid2 = reply_info.formid
                    sendMessage(commodity_id, formid2, information,oauth_bind_info.openid)
                else:
                    resp['code'] = -1
                    resp['msg'] = "reply_info不存在"
                    return jsonify(resp)
                sendMessage(commodity_id,formid1,information,oauth_bind_info.openid)
            except InvalidRequestError:
                db.session.rollback()
    return jsonify(resp)

@route_api.route("/mycollect", methods=["GET", "POST"])
def mycollect():
    resp = {'code': 200, 'msg': '操作成功~', 'dataList': {}}
    req = request.values
    member_id = req['uid'] if 'uid' in req else ''
    page = int(req['p']) if ('p' in req and req['p']) else 1
    if not member_id:
        resp['code'] = -1
        resp['msg'] = "需要member_id"
        return jsonify(resp)
    if not page:
        resp['code'] = -1
        resp['msg'] = "需要page"
        return jsonify(resp)
    offset = (page - 1) * 6
    limit = 6 * page
    Collection_List = MemberCollection.query.filter_by( member_id = member_id ).order_by(MemberCollection.id.desc()).all()[ offset:limit ]
    postsList = []
    if Collection_List:
        for item in Collection_List:
            Commodity_info = CommodityInformation.query.filter_by( id = item.commodity_id ).first()
            str_list = Commodity_info.image
            image_list = str_list.split(',')
            tmp_data = {
                'id': item.id,
                'Commodity_id':Commodity_info.id,
                'title': Commodity_info.name,
                'price': Commodity_info.price,
                'image': image_list[0],
                'status': Commodity_info.status,
                'time': item.created_time
            }
            postsList.append(tmp_data)
    resp['dataList'] = postsList
    resp['has_more'] = 0 if len(postsList) < 6 else 1
    return jsonify(resp)

@route_api.route("/myfabu", methods=["GET", "POST"])
def myfabu():
    resp = {'code': 200, 'msg': '操作成功~', 'dataList': {}}
    req = request.values
    member_id = req['uid'] if 'uid' in req else ''
    page = int(req['p']) if ('p' in req and req['p']) else 1
    if not member_id:
        resp['code'] = -1
        resp['msg'] = "需要member_id"
        return jsonify(resp)
    if not page:
        resp['code'] = -1
        resp['msg'] = "需要page"
        return jsonify(resp)
    offset = (page - 1) * 6
    limit = 6 * page

    Commodity_List = CommodityInformation.query.filter_by( authorId = member_id, status = 1).order_by(CommodityInformation.id.desc()).all()[ offset:limit ]
    postsList = []
    if Commodity_List:
        for item in Commodity_List:
            str_list = item.image
            image_list = str_list.split(',')
            tmp_data = {
                'id': item.id,
                'Commodity_id': item.id,
                'title': item.name,
                'price': item.price,
                'image': image_list[0],
                'status': item.status,
                'time': item.created_time
            }
            postsList.append(tmp_data)
    resp['dataList'] = postsList
    resp['has_more'] = 0 if len(postsList) < 6 else 1
    return jsonify(resp)

@route_api.route("/delcollerct",methods = ["GET","POST"])
def delcollerct():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    collect_id = req['id'] if 'id' in req else ''
    if not collect_id:
        resp['code'] = -1
        resp['msg'] = "需要collect_id"
        return jsonify(resp)
    collect_info = MemberCollection.query.filter_by( id = collect_id ).first()
    db.session.delete(collect_info)
    db.session.commit()
    return jsonify(resp)

@route_api.route("/delcollerct2",methods = ["GET","POST"])
def delcollerct2():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    uid = req['uid'] if 'uid' in req else '1'
    goodsid = req['goodsid'] if 'goodsid' in req else '2'
    if not goodsid:
        resp['code'] = -1
        resp['msg'] = "需要goodsid"
        return jsonify(resp)
    if not uid:
        resp['code'] = -1
        resp['msg'] = "需要uid"
        return jsonify(resp)
    collect_info = MemberCollection.query.filter_by(member_id=uid,commodity_id=goodsid).first()
    db.session.delete(collect_info)
    db.session.commit()
    return jsonify(resp)

@route_api.route("/delfabu",methods = ["GET","POST"])
def delfabu():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    fabu_id = req['id'] if 'id' in req else ''
    if not fabu_id:
        resp['code'] = -1
        resp['msg'] = "需要fabu_id"
        return jsonify(resp)
    fabu_info = CommodityInformation.query.filter_by( id = fabu_id ).first()
    fabu_info.status = 0
    db.session.commit()
    return jsonify(resp)

@route_api.route("/edit",methods = ["GET","POST"])
def edit():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    fabu_id = req['id'] if 'id' in req else ''
    title = req['title'] if 'title' in req else ''
    area = req['area'] if 'area' in req else ''
    describe = req['describe'] if 'describe' in req else ''
    imageList = req['imageList'] if 'imageList' in req else ''
    price = req['price'] if 'price' in req else ''
    QQnum = req['QQnum'] if 'QQnum' in req else ''
    formid = req['formid'] if 'formid' in req else ''
    # str_list = imageList
    # upload_file = str_list.split(',')
    # imageList = []
    # for i in range(len(upload_file)):
    #     ret = UploadService.uploadByFile(upload_file[i], author_id)
    #     url = UrlManager.buildImageUrl(ret["url"])
    #     imageList.append(url)
    # image = ','.join(imageList)

    fabu_info = CommodityInformation.query.filter_by( id = fabu_id ).first()
    fabu_info.name = title
    fabu_info.area_tab = area
    fabu_info.contacts = describe
    fabu_info.image = imageList
    fabu_info.price = price
    fabu_info.qqnumber = QQnum
    fabu_info.formid = formid
    fabu_info.updated_time = getCurrentDate()
    fabu_info.created_time = getCurrentDate()
    db.session.commit()
    return jsonify(resp)


@route_api.route("/fabu",methods = [ "GET","POST" ])
def fabu():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    author_id = req['author_id'] if 'author_id' in req else ''
    tab = req['tab'] if 'tab' in req else ''
    title = req['title'] if 'title' in req else ''
    type = req['type'] if 'type' in req else ''
    area = req['area'] if 'area' in req else ''
    describe = req['describe'] if 'describe' in req else ''
    price = req['price'] if 'price' in req else ''
    phomenum = req['phomenum'] if 'phomenum' in req else ''
    QQnum = req['QQnum'] if 'QQnum' in req else ''
    imageList = req['imageList'] if 'imageList' in req else ''
    formid = req['formid'] if 'formid' in req else ''
    # imageList = "https://jiyikapian.cn//static/upload/8/20190609/c493561d957b4a62baed402478c5b180.jpg,https://jiyikapian.cn//static/upload/88/20190608/18e528644ac6419695cf49d76bf3d5aa.jpg"
    # str_list = imageList
    # upload_file = str_list.split(',')
    # imageList = []
    # for i in range(len(upload_file)):
    #     ret = UploadService.uploadByFile(upload_file[i], author_id)
    #     url = UrlManager.buildImageUrl( ret["url"] )
    #     imageList.append(url)
    # image = ','.join(imageList)
    try:
        Commodity = CommodityInformation()
        Commodity.authorId = author_id
        Commodity.name = title
        Commodity.tab = tab
        Commodity.type = type
        Commodity.area_tab = area
        Commodity.contacts = describe
        Commodity.price = price
        Commodity.phonenumber = phomenum
        Commodity.qqnumber = QQnum
        Commodity.image = imageList
        Commodity.formid = formid
        # Commodity.last_count = 0
        Commodity.updated_time = getCurrentDate()
        Commodity.created_time = getCurrentDate()
        db.session.add(Commodity)
        db.session.commit()
    except InvalidRequestError:
        db.session.rollback()

    return jsonify(resp)

@route_api.route("/upimage",methods = [ "GET","POST" ])
def upimage():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    # resp = {}
    req = request.values
    id = req['id'] if 'id' in req else ''
    if id is None:
        resp['state'] = "id获取失败"
        return jsonify(resp)

    file_target = request.files
    upfile = file_target['image'] if 'image' in file_target else None
    if upfile is None:
        resp['state'] = "上传失败"
        return jsonify(resp)

    ret = UploadService.uploadByFile(upfile, id)
    if ret['code'] != 200:
        resp['state'] = "上传失败：" + ret['msg']
        return jsonify(resp)

    # resp = UrlManager.buildImageUrl(ret['data']['file_key'])
    resp['url'] = UrlManager.buildImageUrl(ret['data']['file_key'])
    return jsonify(resp)

@route_api.route("/member/login", methods=["GET", "POST"])
def login():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    code = req['code'] if 'code' in req else ''
    if not code or len(code) < 1:
        resp['code'] = -1
        resp['msg'] = "需要code"
        return jsonify(resp)

    openid = MemberService.getWeChatOpenId(code)
    if openid is None:
        resp['code'] = -1
        resp['msg'] = "调用微信出错"
        return jsonify(resp)

    # app.logger.info( req )
    try:
        nickname = req['nickName'] if 'nickName' in req else ''
        sex = req['gender'] if 'gender' in req else ''
        avatar = req['avatarUrl'] if 'avatarUrl' in req else ''
        bind_info = OauthMemberBind.query.filter_by(openid=openid, type=1).first()
        # result = re_emojis(nickname)
        text = emoji.demojize(nickname)
        result = re.sub(':\S+?:', ' ', text)
        if not bind_info:
            model_member = Member()
            model_member.nickname = result
            model_member.sex = sex
            model_member.avatar = avatar
            model_member.salt = MemberService.geneSalt()
            model_member.updated_time = model_member.created_time = getCurrentDate()
            db.session.add(model_member)
            db.session.commit()

            model_bind = OauthMemberBind()
            model_bind.member_id = model_member.id
            model_bind.type = 1
            model_bind.openid = openid
            model_bind.extra = ''
            model_bind.updated_time = model_bind.created_time = getCurrentDate()
            db.session.add(model_bind)
            db.session.commit()

            bind_info = model_bind
            member_info = Member.query.filter_by(id=bind_info.member_id).first()

            token = "%s#%s" % (MemberService.geneAuthCode(member_info), member_info.id)

            resp['data'] = {'token': token}

    except InvalidRequestError:
         db.session.rollback()

    return jsonify(resp)

@route_api.route("/member/check-reg",methods = ["GET","POST"])
def checkReg( ):
    resp = {'code':200,'msg':'操作成功~','data':{}}
    req = request.values

    code = req['code'] if 'code' in req else ''
    if not code or len(code)<1:
        resp['code'] = -1
        resp['msg'] ="需要code"
        return jsonify(resp)

    openid = MemberService.getWeChatOpenId(code)
    if openid is None:
        resp['code'] = -1
        resp['msg'] = "调用微信出错"
        return jsonify(resp)

    bind_info = OauthMemberBind.query.filter_by(openid=openid, type=1).first()
    if not bind_info:
        resp['code'] = -1
        resp['msg'] = "未绑定"
        return jsonify(resp)
    member_info = Member.query.filter_by(id=bind_info.member_id).first()
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "未查询到绑定信息"
        return jsonify(resp)
    if (member_info.hjStudentID):
        resp['stuid'] = member_info.hjStudentID

    token = "%s#%s"%( MemberService.geneAuthCode( member_info ), member_info.id )
    resp['data'] = { 'token':token }
    return jsonify(resp)

@route_api.route("/renzhen", methods=["GET", "POST"])
def renzheng():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    uid = req['uid'] if 'uid' in req else ''
    idnum = req['idnum'] if 'idnum' in req else ''
    password = req['password'] if 'password' in req else ''
    member_info = Member.query.filter_by(hjStudentID=idnum).first()

    if (idnum == "2021211001000314"):
        member_info = Member.query.filter_by(id=uid).first()
        member_info.hjStudentID = idnum
        db.session.commit()
        resp['stuid'] = idnum
    else:
        if member_info:
            resp['code'] = -1
            resp['msg'] = "此学号已被认证"
            return jsonify(resp)
        username = idnum
        password = password
        # print(common.libs.ASSE.main(username, password, uid))
        is_renzheng = common.libs.ASSE.main(username, password, uid)
        if (is_renzheng == "success"):
            member_info = Member.query.filter_by(id=uid).first()
            member_info.hjStudentID = idnum
            db.session.commit()
            resp['stuid'] = idnum
        else:
            resp['code'] = -1
            resp['msg'] = "用户名或密码错误"
            return jsonify(resp)
    return jsonify(resp)

@route_api.route("/delword", methods=["GET", "POST"])
def delword():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    word_id = req['id'] if 'id' in req else ''
    word_info = LeavingWord.query.filter_by(id=word_id).first()
    Commodity_info = CommodityInformation.query.filter_by(id=word_info.commidity_id).first()
    Commodity_info.last_count = int(Commodity_info.last_count)-1
    db.session.delete(word_info)
    db.session.commit()
    return jsonify(resp)

@route_api.route("/index_image", methods=["GET", "POST"])
def index_image():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    swiperList= [{
        'id': 0,
        'type': 'image',
        'url': 'http://www.yun360.xyz/assets/img-temp/600x350/img5.jpg'
    }, {
        'id': 1,
        'type': 'image',
        'url': 'http://www.yun360.xyz/assets/img-temp/600x350/img3.jpg',
    }, {
        'id': 2,
        'type': 'image',
        'url': 'http://www.yun360.xyz/assets/img-temp/600x350/img6.jpg'
    }, {
        'id': 3,
        'type': 'image',
        'url': 'http://www.yun360.xyz/assets/img-temp/600x350/img10.jpg'
    }, {
        'id': 4,
        'type': 'image',
        'url': 'http://www.yun360.xyz/assets/img-temp/600x350/img12.jpg'
    }, {
        'id': 5,
        'type': 'image',
        'url': 'http://img.mp.itc.cn/upload/20160820/47c78b1df9ed4e6e93f23788df09be5b_th.jpeg'
    }, {
        'id': 6,
        'type': 'image',
        'url': 'http://www.yun360.xyz/assets/img-temp/600x350/img4.jpg'
    }]
    resp['swiperList'] = swiperList
    return jsonify(resp)

@route_api.route("/search", methods=["GET", "POST"])
def search():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    # word_id = req['id'] if 'id' in req else ''
    mix_kw = str(req['mix_kw']) if 'mix_kw' in req else ''
    page = int(req['p']) if ('p' in req and req['p']) else 1
    offset = (page - 1) * 6
    limit = 6 * page
    query = CommodityInformation.query.filter_by(status=1)
    if mix_kw:
        rule = or_(CommodityInformation.name.ilike("%{0}%".format(mix_kw)), CommodityInformation.contacts.ilike("%{0}%".format(mix_kw)), CommodityInformation.area_tab.ilike("%{0}%".format(mix_kw)), CommodityInformation.type.ilike("%{0}%".format(mix_kw)), CommodityInformation.tab.ilike("%{0}%".format(mix_kw)))
        query = query.filter(rule)
    Commodity_List = query.all()[ offset:limit ]
    postsList = []
    if Commodity_List:
        for item in Commodity_List:
            reply_count = LeavingWord.query.filter_by(commidity_id=item.id).count()
            author = Member.query.filter_by(id=item.authorId).first()
            str_list = item.image
            image_list = str_list.split(',')
            imageList = []
            for i in range(len(image_list)):
                image_data = {
                    'id': i,
                    'type': 'image',
                    'url': image_list[i]
                }
                imageList.append(image_data)
            print(imageList)
            tmp_data = {
                'id': item.id,
                'title': item.name,
                'author_id': item.authorId,
                'price': item.price,
                'visit_count': item.view_count,
                'reply_count': reply_count,
                'type': item.type,
                'create_at': item.created_time,
                'imageList': imageList,
                'area_tab': item.area_tab,
                'author': {
                    'loginname': author.nickname,
                    'avatar_url': author.avatar
                }
            }
            postsList.append(tmp_data)
    resp['postsList'] = postsList
    resp['has_more'] = 0 if len(postsList) < 6 else 1
    return jsonify(resp)

@route_api.route("/resetFormid", methods=["GET", "POST"])
def resetFormid():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    commodity_id = req['commodity_id'] if 'commodity_id' in req else ''
    formid = req['formid'] if 'formid' in req else ''
    if not commodity_id:
        resp['code'] = -1
        resp['msg'] = "需要Commodity_id"
        return jsonify(resp)
    if not formid:
        resp['code'] = -1
        resp['msg'] = "需要formid"
        return jsonify(resp)
    commodity_info = CommodityInformation.query.filter_by( status = 1, id = commodity_id).first()
    if not commodity_info:
        resp['code'] = -1
        resp['msg'] = "商品已无效"
        return jsonify(resp)
    reply_count = LeavingWord.query.filter_by(commidity_id=commodity_info.id).count()
    try:
        commodity_info.formid = formid
        commodity_info.last_count = reply_count
        db.session.commit()
    except InvalidRequestError:
        db.session.rollback()
    return jsonify(resp)

@route_api.route("/resetTime", methods=["GET", "POST"])
def resetTime():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    commodity_id = req['commodity_id'] if 'commodity_id' in req else ''
    if not commodity_id:
        resp['code'] = -1
        resp['msg'] = "需要Commodity_id"
        return jsonify(resp)
    commodity_info = CommodityInformation.query.filter_by(status=1, id=commodity_id).first()
    if not commodity_info:
        resp['code'] = -1
        resp['msg'] = "商品已无效"
        return jsonify(resp)
    try:
        commodity_info.updated_time = getCurrentDate()
        db.session.commit()
    except InvalidRequestError:
        db.session.rollback()
    return jsonify(resp)

@route_api.route("/tuisong", methods=["GET", "POST"])
def tuisong():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    offset = int(1001)
    limit = int(2211)
    member_info = Member.query.filter_by().all() [ offset:limit ]
    target_wechat = WeChatService( )
    access_token = target_wechat.getAccessToken()
    print(access_token)
    # member_info = Member.query.filter_by().all()
    if member_info:
        for item in member_info:
            bind_info = OauthMemberBind.query.filter_by(member_id = item.id).first()
            if(bind_info):
                openid = bind_info.openid
                sendDingYue(openid,access_token)
    return jsonify(resp)

def re_emojis(text):
    emoji_pattern = re.compile("["
           u"\U0001F600-\U0001F64F"
           u"\U0001F300-\U0001F5FF"
           u"\U0001F680-\U0001F6FF"
           u"\U0001F1E0-\U0001F1FF"
           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r' ', text)

def sendMessage( id,formid,information,openid ):
    commodity_id = id
    if not id:
        return False

    commodity_info = CommodityInformation.query.filter_by(id = commodity_id).first()
    # member_id  = commodity_info.authorId
    # oauth_bind_info = OauthMemberBind.query.filter_by(member_id = member_id).first()
    # member_info = Member.query.filter_by(id = member_id).first()
    #     # if not oauth_bind_info:
    #     #     return False

    keyword1_val = str(commodity_info.name)
    keyword2_val = information
    # keyword3_val = str(member_info.nickname)
    keyword3_val = getCurrentDate()
    commodity_info_ID = commodity_info.id
    page = "/pages/detail/detail?id=%s&isshare=1"%(commodity_info_ID)

    #发送模板消息
    target_wechat = WeChatService( )
    access_token = target_wechat.getAccessToken()
    headers = {'Content-Type': 'application/json'}
    # url = "https://api.q.qq.com/api/json/subscribe/SendSubscriptionMessage?access_token=%s"%access_token
    url = "https://api.q.qq.com/api/json/template/send?access_token=%s"%access_token
    params = {
        "appid" : "1109811211",
        "touser": openid,
        # "template_id":"a4c97a4a5701cdf9deac1d1f2e371a5e",
        "template_id":"4477e4d327dc382671ae56ded9611448",
        "page": page,
        "form_id": formid,
        "data": {
            "keyword1": {
                "value": keyword1_val
            },
            "keyword2": {
                "value": keyword2_val
            },
            "keyword3": {
                "value": keyword3_val
            },
            # "keyword4": {
            #     "value": keyword4_val
            # }
        }
    }

    r = requests.post(url=url, data= json.dumps( params ).encode('utf-8'), headers=headers)
    r.encoding = "utf-8"
    print(r.text)
    return True

def sendDingYue( openid,access_token ):
    keyword1_val = 'ios系统无法发布商品问题'
    keyword2_val = '可在微信版发布'
    keyword3_val = '点击即可查看微信版入口！最近毕业“捡漏季”平台超多好物等你pick'
    page = "/pages/datadetail/datadetail?id=10"

    #发送模板消息
    # target_wechat = WeChatService( )
    # access_token = target_wechat.getAccessToken()
    # print(access_token)
    headers = {'Content-Type': 'application/json'}
    url = "https://api.q.qq.com/api/json/subscribe/SendSubscriptionMessage?access_token=%s"%access_token
    params = {
        "appid" : "1109811211",
        "touser": openid,
        "template_id":"6023cbbf264e27bd660e5c46a8b341b6",
        "page": page,
        "data": {
            "keyword1": {
                "value": keyword1_val
            },
            "keyword2": {
                "value": keyword2_val
            },
            "keyword3": {
                "value": keyword3_val
            }
        }
    }
    r = requests.post(url=url, data= json.dumps( params ).encode('utf-8'), headers=headers)
    r.encoding = "utf-8"
    print(r.text)
    return True
