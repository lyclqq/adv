# -*- coding: utf-8 -*-
from flask import Blueprint,render_template,current_app,url_for,redirect,session,request,flash,g
from app.models.contract import Orders
 #合同搜索
def search_orders(searchform,page):
    searchform.status.choices = [('全部', '全部'), ('己审', '己审'), ('未审', '未审'), ('待审', '待审'), ('完成', '完成'),
                           ('作废', '作废')]
    orders=Orders()
    if searchform.validate_on_submit():
        page=1
        title=searchform.title.data
        status=searchform.status.data
        session['order_title']=title
        session['order_status']=status
    else:
        title = session.get('order_title')
        status = session.get('order_status')
        if title is not None:
            searchform.title.data = title
        if status is not None:
            searchform.status.data = status
    pagination=orders.search_orders(keywords=title,status=status,page=page)
    return pagination,page
