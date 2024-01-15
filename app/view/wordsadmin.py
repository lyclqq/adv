# -*- coding: utf-8 -*-

from flask import Blueprint,render_template,current_app,url_for,redirect,session,request,flash,g
import json
import os
from functools import wraps
from app.common import is_login,ins_logs,month_difference
from app.view import search_orders
from app import db
from app.models.contract import Customers,Orders
from app.models.system import Systeminfo
from app.models.bill import Wordnumbers
from app.forms.customer import CustomerForm
from app.forms.order import OrderForm,OrderSearchForm,OrderupfileForm
from app.forms.fee import WordsForm
import datetime

wordsadminView=Blueprint('words_admin',__name__)


#合同查询
@wordsadminView.route('/order_search',methods=["GET","POST"])
@is_login
def order_search():
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    form=OrderSearchForm()
    pagination,page=search_orders(searchform=form,page=page)

    result=pagination.items
    return render_template('wordsadmin/order_search.html', page=page, pagination=pagination, posts=result,form=form)

#合同字数输入
@wordsadminView.route('/words_order/<int:oid>',methods=["GET","POST"])
@is_login
def words_order(oid):
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    form=WordsForm()
    order = Orders.query.filter(Orders.id == oid).first_or_404()
    if order.status != '己审' and order.status!='完成':
        form.submit.render_kw={'class':'form-control','disabled':'true'}
    else:
        form.submit.render_kw = {'class': 'form-control'}
    if form.validate_on_submit():
        systeminfo = Systeminfo.query.filter(Systeminfo.id == 1).first()
        if month_difference(systeminfo.systemmonth, form.fee_date.data) >= 1:
            flash('不能晚于系统当月！.', 'success')
        else:
            try:
                wordnumber=Wordnumbers()
                wordnumber.order_id=oid
                wordnumber.feedate = form.fee_date.data
                wordnumber.status = 'stay'
                wordnumber.wordnumber=form.words.data
                wordnumber.type = 'order'
                wordnumber.iuser_id = uid
                db.session.add(wordnumber)

                db.session.commit()
                flash('录入成功.', 'success')
                ins_logs(uid, '合同字数录入,id=' + str(oid), type='words_admin')
            except Exception as e:
                current_app.logger.error(e)
                flash('录入失败')
    pagination = Wordnumbers.query.filter(Wordnumbers.type == 'order',Wordnumbers.order_id==oid).order_by(Wordnumbers.id.desc()).paginate(page,
                                                                                per_page=8)
    return render_template('wordsadmin/words_input.html', form=form,order=order,pagination=pagination,page=page)

#出版字数输入
@wordsadminView.route('/words_publish/<int:oid>',methods=["GET","POST"])
@is_login
def words_publish(oid):
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    form=WordsForm()
    order = Orders.query.filter(Orders.id == oid).first_or_404()
    if order.status != '己审' and order.status!='完成':
        form.submit.render_kw={'class':'form-control','disabled':'true'}
    else:
        form.submit.render_kw = {'class': 'form-control'}
    if form.validate_on_submit():
        wordnumber=Wordnumbers()
        wordnumber.order_id=oid
        wordnumber.feedate = form.fee_date.data
        wordnumber.status = 'stay'
        wordnumber.wordnumber=form.words.data
        wordnumber.type = 'publish'
        wordnumber.iuser_id=uid
        words=order.wordcount+form.words.data
        db.session.add(wordnumber)
        if words>=0:
            try:
                db.session.commit()
                flash('录入成功.', 'success')
                ins_logs(uid, '出版字数录入,id=' + str(oid), type='words_admin')
            except Exception as e:
                current_app.logger.error(e)
                flash('录入失败')
        else:
            flash('字数余额不能小于0!')
    pagination = Wordnumbers.query.filter(Wordnumbers.type == 'publish',Wordnumbers.order_id==oid).order_by(Wordnumbers.id.desc()).paginate(page, per_page=8)
    return render_template('wordsadmin/words_input.html', form=form,order=order,pagination=pagination,page=page)

#出版字数
@wordsadminView.route('/words_search/<type>')
@is_login
def words_search(type):
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    pagerows = current_app.config['PAGEROWS']
    pagination = Wordnumbers.query.filter(Wordnumbers.type == type).order_by(Wordnumbers.id.desc()).paginate(page, per_page=pagerows)
    return render_template('wordsadmin/words_search.html', pagination=pagination,page=page)