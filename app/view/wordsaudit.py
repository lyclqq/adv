# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, current_app, url_for, redirect, session, request, flash, g
import json
import os
from functools import wraps
from app.common import is_login, ins_logs,search_order
from app import db
from app.models.contract import Customers, Orders
from app.models.other import Files
from app.models.bill import Wordnumbers
from app.forms.customer import CustomerForm
from app.forms.order import OrderForm, OrderSearchForm, OrderupfileForm
from app.forms.fee import WordsForm
import datetime

wordsauditView = Blueprint('words_audit', __name__)


# 合同查询
@wordsauditView.route('/order_search', methods=["GET", "POST"])
@is_login
def order_search():
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    form=OrderSearchForm()
    pagination,form,page=search_order(searchform=form,page=page)

    result = pagination.items
    return render_template('wordsaudit/order_search.html', page=page, pagination=pagination, posts=result, form=form)


# 合同字数审核
@wordsauditView.route('/words_order/<int:oid>')
@is_login
def words_order(oid):
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    order = Orders.query.filter(Orders.id == oid).first_or_404()

    pagination = Wordnumbers.query.filter(Wordnumbers.type == 'order', Wordnumbers.order_id == oid).order_by(
        Wordnumbers.id.desc()).paginate(page,
                                        per_page=8)
    return render_template('wordsaudit/words_show.html', order=order, pagination=pagination, page=page,type='order')


# 出版字数审核
@wordsauditView.route('/words_publish/<int:oid>')
@is_login
def words_publish(oid):
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    order = Orders.query.filter(Orders.id == oid).first_or_404()
    pagination = Wordnumbers.query.filter(Wordnumbers.type == 'publish', Wordnumbers.order_id == oid).order_by(
    Wordnumbers.id.desc()).paginate(page, per_page=8)
    return render_template('wordsaudit/words_show.html', order=order, pagination=pagination, page=page,type='publish')

#字数审核同意
@wordsauditView.route('/wordscount_audit_on/<int:oid>/<int:fid>/<type>')
@is_login
def wordscount_audit_on(oid,fid,type='publish'):
    uid = session.get('user_id')
    wordnumbers=Wordnumbers.query.filter(Wordnumbers.id==fid,Wordnumbers.type==type).first_or_404()
    order = Orders.query.filter(Orders.id == oid).first_or_404()
    diff=0 #合同字数与出版字数的差
    if type=='order':
        total = order.wordnumber + wordnumbers.wordnumber
    else:
        total=order.wordcount+wordnumbers.wordnumber
        diff=order.wordnumber-total
    if wordnumbers.status=='stay' and total>=0 and diff>=0:
        try:
            order.update_datetime=datetime.datetime.now()
            if type=='order':
                order.wordnumber=total
            else:
                order.wordcount=total
            db.session.add(order)
            wordnumbers.status='on'
            wordnumbers.cuser_id=uid
            db.session.add(wordnumbers)
            db.session.commit()
            ins_logs(uid, '字数审核同意，orderid=' + oid, type='wordsaudit')
        except Exception as e:
            current_app.logger.error(e)
            flash('提交失败')
    else:
        flash('不符合条件！')
    if type=='order':
        return redirect(url_for('words_audit.words_order', oid=oid, type=type))
    else:
        return redirect(url_for('words_audit.words_publish',oid=oid,type=type))

#字数审核拒绝
@wordsauditView.route('/wordscount_audit_off/<int:oid>/<int:fid>/<type>')
@is_login
def wordscount_audit_off(oid,fid,type='publish'):
    uid = session.get('user_id')
    wordnumbers=Wordnumbers.query.filter(Wordnumbers.id==fid,Wordnumbers.type==type).first_or_404()
    if wordnumbers.status=='stay' :
        try:
            wordnumbers.status='off'
            wordnumbers.cuser_id=uid
            db.session.add(wordnumbers)
            db.session.commit()
            ins_logs(uid, '字数审核不同意，orderid=' + oid, type='wordsaudit')
        except Exception as e:
            current_app.logger.error(e)
            flash('提交失败')
    else:
        flash('不符合条件！')
    if type=='order':
        return redirect(url_for('words_audit.words_order', oid=oid, type=type))
    else:
        return redirect(url_for('words_audit.words_publish',oid=oid,type=type))

# 出版字数
@wordsauditView.route('/words_search/<type>')
@is_login
def words_search(type):
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    pagerows = current_app.config['PAGEROWS']
    pagination = Wordnumbers.query.filter(Wordnumbers.type == type).order_by(Wordnumbers.id.desc()).paginate(page,
                                                                                                             per_page=pagerows)
    return render_template('wordsaudit/words_search.html', pagination=pagination, page=page)
