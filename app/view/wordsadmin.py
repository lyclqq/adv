# -*- coding: utf-8 -*-

from flask import Blueprint,render_template,current_app,url_for,redirect,session,request,flash,g
import json
import os
from functools import wraps
from app.common import is_login,ins_logs
from app import db
from app.models.contract import Customers,Orders
from app.models.other import Files
from app.forms.customer import CustomerForm
from app.forms.order import OrderForm,OrderSearchForm,OrderupfileForm
import datetime

wordsadminView=Blueprint('words_admin',__name__)


#合同查询
@wordsadminView.route('/order_search',methods=["GET","POST"])
@is_login
def order_search():
    uid = session.get('user_id')
    form=OrderSearchForm()

    page = request.args.get('page', 1, type=int)
    orders=Orders()
    if form.validate_on_submit():
        title=form.title.data
        status=form.status.data
        pagination=orders.search_orders( keywords=title,status=status,page=1)
    else:
        pagination=orders.search_orders(None,page=page)
    form.status.choices=[('全部','全部'),('己审','己审' ), ('未审','未审' ),( '待审','待审'), ('完成', '完成'),('作废', '作废')]
    #pagination=orders.query.paginate(page, per_page=current_app.config['PAGEROWS'])
    result=pagination.items
    return render_template('wordsadmin/order_search.html', page=page, pagination=pagination, posts=result,form=form)

#字数输入
@wordsadminView.route('/words_input',methods=["GET","POST"])
@is_login
def words_input(oid):
    pass

#字数查看
@wordsadminView.route('/words_show',methods=["GET","POST"])
@is_login
def words_show(oid):
    pass