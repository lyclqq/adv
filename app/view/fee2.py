# -*- coding: utf-8 -*-

from flask import Blueprint,render_template,current_app,url_for,redirect,session,request,flash,g
import json
import os
from functools import wraps
from app.common import is_login,ins_logs
from app import db
from app.models.contract import Customers,Orders
from app.models.other import Files
from app.models.bill import Wordnumbers,Fee1,Fee2
from app.forms.customer import CustomerForm
from app.forms.fee import FeeForm,AuditForm
from app.forms.order import OrderForm,OrderSearchForm,OrderupfileForm
import datetime

fee2View=Blueprint('fee2',__name__)

#合同查询为管理
@fee2View.route('/order_search_admin',methods=["GET","POST"])
@is_login
def order_search_admin():
    uid = session.get('user_id')
    form=OrderSearchForm()
    form.status.choices = [('全部', '全部'), ('己审', '己审'), ('未审', '未审'), ('待审', '待审'), ('完成', '完成'),
                           ('作废', '作废')]
    page = request.args.get('page', 1, type=int)
    orders=Orders()
    if form.validate_on_submit():

        title=form.title.data
        status=form.status.data
        pagination=orders.search_orders( keywords=title,status=status,page=1)
    else:
        pagination=orders.search_orders(None,page=page)

    #pagination=orders.query.paginate(page, per_page=current_app.config['PAGEROWS'])
    result=pagination.items
    return render_template('fee2/order_search_admin.html', page=page, pagination=pagination, posts=result,form=form)

#刊登金额输入
@fee2View.route('/fee2_input/<int:oid>',methods=["GET","POST"])
@is_login
def fee2_input(oid):
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    form= FeeForm()
    order = Orders.query.filter(Orders.id == oid).first_or_404()
    if form.validate_on_submit():
        fee2=Fee2()
        fee2.order_id=oid
        fee2.feedate = form.fee_date.data
        fee2.status = 'stay'
        fee2.fee=form.fee.data
        fee2.iuser_id=uid
        total=order.Fee21+form.fee.data
        db.session.add(fee2)
        if total>=0:
            try:
                db.session.commit()
                flash('录入成功.', 'success')
                ins_logs(uid, '刊登金额录入,id=' + str(oid), type='fee2')
            except Exception as e:
                current_app.logger.error(e)
                flash('录入失败')
        else:
            flash('余额不能小于0!')
    pagination = Fee2.query.filter(Fee2.order_id==oid).order_by(Fee2.id.desc()).paginate(page, per_page=8)
    return render_template('fee2/fee2_input.html', form=form,order=order,pagination=pagination,page=page)

@fee2View.route('/fee2_search_admin')
@is_login
def fee2_search_admin():
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    pagerows = current_app.config['PAGEROWS']
    pagination = Fee2.query.order_by(Fee2.id.desc()).paginate(page, per_page=pagerows)
    return render_template('fee2/fee2_search_admin.html', pagination=pagination,page=page)

@fee2View.route('/fee2_search_audit')
@is_login
def fee2_search_audit():
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    pagerows = current_app.config['PAGEROWS']
    pagination = Fee2.query.order_by(Fee2.id.desc()).paginate(page, per_page=pagerows)
    return render_template('fee2/fee2_search_udit.html', pagination=pagination,page=page)


#刊登金额审核
@fee2View.route('/fee2_audit/<int:fid>',methods=["GET","POST"])
@is_login
def fee2_audit(fid):
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    form= AuditForm()
    fee2=Fee2.query.filter(Fee2.id==fid).first_or_404()
    order = Orders.query.filter(Orders.id == fee2.order_id).first_or_404()
    if form.validate_on_submit():
        total=order.Fee21+form.fee.data
        if total>=0:
            try:
                fee2.status = form.status.data
                fee2.cuser_id=uid
                db.session.add(fee2)
                order.Fee21=total
                order.update_datetime=datetime.datetime.now()
                db.session.add(order)
                db.session.commit()
                flash('审核成功.', 'success')
                ins_logs(uid, '刊登金额审核,id=' + str(oid), type='fee2')
            except Exception as e:
                current_app.logger.error(e)
                flash('审核失败')
        else:
            flash('余额不能小于0!')

    return render_template('fee2/fee2_audit.html', form=form,order=order,page=page)