# -*- coding: utf-8 -*-
from flask import Blueprint,render_template,current_app,url_for,redirect,session,request,flash,g
import json
import os
from functools import wraps
from app.models.system import Logs,Systeminfo
from app.models.contract import Orders
from app import db
from app.forms.order import OrderSearchForm
import datetime
#登陆验证
def is_login(view_func):
    @wraps(view_func)
    def wrapper(*args,**kwargs):
        if str(session.get('username')) != 'None':
            g.user_id = session.get("user_id")
            g.username = session.get('username')
            g.menu=getmenu(session.get('usermenu'))
            session['menu'] = getmenu(session.get('usermenu'))
        else:
            return redirect(url_for('login'))
        return view_func(*args,**kwargs)
    return wrapper

def getmenu(usermenu='00000000000000'):
    #从menu.json文件读取所有菜单
    strpath=os.getcwd()+"\\app\\static\\menu.json"
    with open(strpath, 'r', encoding='utf-8_sig') as f:
        allmenu = json.load(f)
    menu = []
    #按照菜单权限生成用户菜单
    for item in allmenu:
        ii = item.get('id')
        if usermenu[ii] == '1':
            menu.append(item)
    return menu

#获取角色的菜单权限
def getrolemenu(rolename):
    strpath = os.getcwd() + "\\app\\static\\role.json"
    with open(strpath, 'r', encoding='utf-8_sig') as f:
        roles=json.load(f)
    for item in roles:
        if item.get("role")==rolename:
            return item.get("menu")

    return "00000000000000"

#写日志
def ins_logs(userid,notes,type='system'):
    tf=False
    logs=Logs()
    ip=request.remote_addr
    logs.user_id=userid
    logs.ip=ip
    logs.notes=notes
    logs.type=type
    try:
        db.session.add(logs)
        db.session.commit()
        tf=True
    except Exception as e:
        current_app.logger.error(e)
    return tf

#比较月份
def month_difference(date1, date2):
    if type(date1)!=datetime.date:
        date1=datetime.datetime.strptime(date1, "%Y-%m-%d")
    if type(date2)!=datetime.date:
        date2=datetime.datetime.strptime(date2, "%Y-%m-%d")
    diff = date2.year * 12 + date2.month - (date1.year * 12 + date1.month)
    return diff

#获取系统当月
def get_month():
    systeminfo=Systeminfo.query.filter(Systeminfo.id==1).first()
    return systeminfo.systemmonth




