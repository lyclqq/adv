# -*- coding: utf-8 -*-
from flask import Blueprint,render_template,current_app,url_for,redirect,session,request,flash,g
import json
import os
from functools import wraps

#登陆验证
def is_login(view_func):
    @wraps(view_func)
    def wrapper(*args,**kwargs):
        if str(session.get('username')) != 'None':
            g.user_id = session.get("user_id")
            g.username = session.get('username')
            g.menu=getmenu(session.get('usermenu'))
        else:
            return redirect(url_for('login'))
        return view_func(*args,**kwargs)
    return wrapper

def getmenu(usermenu='00000000'):
    #从menu.json文件读取所有菜单
    strpath=os.getcwd()+"\\app\\static\\menu.json"
    with open(strpath, 'r') as f:
        allmenu = json.load(f)
    #f = open(strpath, 'r')
    #allmenu = json.loads(f.readline())
    print(allmenu)
    menu = []
    #按照菜单权限生成用户菜单
    for item in allmenu:
        ii = item.get('id')
        print(ii)
        if usermenu[ii] == '1':
            menu.append(item)
    print(menu)
    return menu