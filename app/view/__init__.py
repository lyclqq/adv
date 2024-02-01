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
    if session.get('type')=='admin' or session.get('type')=='input1' or session.get('type')=='input2' or session.get('type')=='input3':
        groupid=0
    else:
        groupid=session.get('group_id')
    pagination=orders.search_orders(keywords=title,status=status,page=page,groupid=groupid)
    return pagination,page

class echarts():
    class title():
        test='this is map'

    class legend():
        data=['销量']

    class xAxis():
        data= ['衬衫', '羊毛衫', '雪纺衫', '裤子', '高跟鞋', '袜子']


    series= [  {
            'name': '销量',
            'type': 'bar',
            'data': [5, 20, 36, 10, 10, 20]
          }]
