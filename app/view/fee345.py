# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, current_app, url_for, redirect, session, request, flash, g
import json
import os
from functools import wraps
from app.common import is_login, ins_logs
from app import db
from app.models.contract import Customers, Orders
from app.models.other import Files
from app.models.bill import Wordnumbers, Fee1, Fee2, Fee3, Fee4, Fee5
from app.forms.customer import CustomerForm
from app.forms.fee import Fee2Form, AuditForm, Fee3Form
from app.forms.order import OrderForm, OrderSearchForm, OrderupfileForm
import datetime

fee345View = Blueprint('fee345', __name__)


# 合同查询为管理
@fee345View.route('/order_search_admin', methods=["GET", "POST"])
@is_login
def order_search_admin():
    uid = session.get('user_id')
    form = OrderSearchForm()
    form.status.choices = [('全部', '全部'), ('己审', '己审'), ('未审', '未审'), ('待审', '待审'), ('完成', '完成'),
                           ('作废', '作废')]
    page = request.args.get('page', 1, type=int)
    orders = Orders()
    if form.validate_on_submit():

        title = form.title.data
        status = form.status.data
        pagination = orders.search_orders(keywords=title, status=status, page=1)
    else:
        pagination = orders.search_orders(None, page=page)

    # pagination=orders.query.paginate(page, per_page=current_app.config['PAGEROWS'])
    result = pagination.items
    return render_template('fee345/order_search_admin.html', page=page, pagination=pagination, posts=result, form=form)

# 合同查询为管理
@fee345View.route('/order_search_audit', methods=["GET", "POST"])
@is_login
def order_search_audit():
    uid = session.get('user_id')
    form = OrderSearchForm()
    form.status.choices = [('全部', '全部'), ('己审', '己审'), ('未审', '未审'), ('待审', '待审'), ('完成', '完成'),
                           ('作废', '作废')]
    page = request.args.get('page', 1, type=int)
    orders = Orders()
    if form.validate_on_submit():

        title = form.title.data
        status = form.status.data
        pagination = orders.search_orders(keywords=title, status=status, page=1)
    else:
        pagination = orders.search_orders(None, page=page)

    # pagination=orders.query.paginate(page, per_page=current_app.config['PAGEROWS'])
    result = pagination.items
    return render_template('fee345/order_search_audit.html', page=page, pagination=pagination, posts=result, form=form)

# 刊登金额输入
@fee345View.route('/fee5_input/<int:oid>', methods=["GET", "POST"])
@is_login
def fee5_input(oid):
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    form = Fee2Form()
    order = Orders.query.filter(Orders.id == oid).first_or_404()
    if form.validate_on_submit():
        fee2 = Fee2()
        fee2.order_id = oid
        fee2.feedate = form.fee_date.data
        fee2.status = 'stay'
        fee2.fee = form.fee.data
        fee2.area = form.area.data
        fee2.iuser_id = uid
        total = order.Fee21 + form.fee.data
        fee2.notes = form.notes.data

        if total >= 0:
            try:
                db.session.add(fee2)
                db.session.commit()
                flash('录入成功.', 'success')
                ins_logs(uid, '刊登金额录入,id=' + str(oid), type='fee2')
            except Exception as e:
                current_app.logger.error(e)
                flash('录入失败')
        else:
            flash('余额不能小于0!')
    pagination = Fee2.query.filter(Fee2.order_id == oid).order_by(Fee2.id.desc()).paginate(page, per_page=8)
    return render_template('fee345/fee3_input.html', form=form, order=order, pagination=pagination, page=page)


# 刊登金额输入
@fee345View.route('/fee4_input/<int:oid>', methods=["GET", "POST"])
@is_login
def fee4_input(oid):
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    form = Fee3Form()
    order = Orders.query.filter(Orders.id == oid).first_or_404()
    if form.validate_on_submit():
        try:
            fee4 = Fee4()
            fee4.order_id = oid
            fee4.feedate = form.fee_date.data
            fee4.status = 'stay'
            fee4.fee = form.fee.data
            fee4.iuser_id = uid
            total = order.Fee41 + form.fee.data
            fee4.notes = form.notes.data
            if total >= 0:
                f = request.files.get('upfile')
                if f:
                    extension = f.filename.split('.')[-1].lower()
                    if extension not in ['doc', 'xls', 'docx', 'xlsx', 'pdf']:
                        flash('只能上传pdf、word和excel文件!')
                    else:
                        newfilename = session.get('username') + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                        path = os.path.join(current_app.config['UPLOADED_PATH'],
                                        datetime.datetime.now().strftime("%Y") + os.sep)
                        if not os.path.exists(path):
                            os.mkdir(path)
                        f.save(os.path.join(path, newfilename + '.' + extension))
                        fee4.path=datetime.datetime.now().strftime("%Y") + os.sep
                        fee4.filename=newfilename+'.'+extension
                db.session.add(fee4)
                db.session.commit()
                flash('录入成功.', 'success')
                ins_logs(uid, '到帐金额录入,id=' + str(oid), type='fee345')
            else:
                flash('余额不能小于0!')
        except Exception as e:
            current_app.logger.error(e)
            flash('录入失败')
    pagination = Fee4.query.filter(Fee4.order_id == oid).order_by(Fee4.id.desc()).paginate(page, per_page=8)
    return render_template('fee345/fee4_input.html', form=form, order=order, pagination=pagination, page=page)


# 发票金额输入
@fee345View.route('/fee3_input/<int:oid>', methods=["GET", "POST"])
@is_login
def fee3_input(oid):
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    form = Fee3Form()
    order = Orders.query.filter(Orders.id == oid).first_or_404()
    if form.validate_on_submit():
        try:
            fee3 = Fee3()
            fee3.order_id = oid
            fee3.feedate = form.fee_date.data
            fee3.status = 'stay'
            fee3.fee = form.fee.data
            fee3.iuser_id = uid
            total = order.Fee31 + form.fee.data
            fee3.notes = form.notes.data
            if total >= 0:
                f = request.files.get('upfile')
                if f:
                    extension = f.filename.split('.')[-1].lower()
                    if extension not in ['doc', 'xls', 'docx', 'xlsx', 'pdf']:
                        flash('只能上传pdf、word和excel文件!')
                    else:
                        newfilename = session.get('username') + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                        path = os.path.join(current_app.config['UPLOADED_PATH'],
                                        datetime.datetime.now().strftime("%Y") + os.sep)
                        if not os.path.exists(path):
                            os.mkdir(path)
                        f.save(os.path.join(path, newfilename + '.' + extension))
                        fee3.path=datetime.datetime.now().strftime("%Y") + os.sep
                        fee3.filename=newfilename+'.'+extension
                db.session.add(fee3)
                db.session.commit()
                flash('录入成功.', 'success')
                ins_logs(uid, '发票金额录入,id=' + str(oid), type='fee345')
            else:
                flash('余额不能小于0!')
        except Exception as e:
            current_app.logger.error(e)
            flash('录入失败')
    pagination = Fee3.query.filter(Fee3.order_id == oid).order_by(Fee3.id.desc()).paginate(page, per_page=8)
    return render_template('fee345/fee3_input.html', form=form, order=order, pagination=pagination, page=page)


#发票金额列表
@fee345View.route('/fee3_search_admin')
@is_login
def fee3_search_admin():
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    pagerows = current_app.config['PAGEROWS']
    pagination = Fee3.query.order_by(Fee3.id.desc()).paginate(page, per_page=pagerows)
    return render_template('fee345/fee3_search_admin.html', pagination=pagination,page=page)

#到帐金额列表
@fee345View.route('/fee4_search_admin')
@is_login
def fee4_search_admin():
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    pagerows = current_app.config['PAGEROWS']
    pagination = Fee4.query.order_by(Fee4.id.desc()).paginate(page, per_page=pagerows)
    return render_template('fee345/fee4_search_admin.html', pagination=pagination,page=page)

@fee345View.route('/fee3_search_audit')
@is_login
def fee3_search_audit():
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    pagerows = current_app.config['PAGEROWS']
    pagination = Fee3.query.order_by(Fee3.id.desc()).paginate(page, per_page=pagerows)
    return render_template('fee345/fee3_search_audit.html', pagination=pagination,page=page)

@fee345View.route('/fee4_search_audit')
@is_login
def fee4_search_audit():
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    pagerows = current_app.config['PAGEROWS']
    pagination = Fee4.query.order_by(Fee4.id.desc()).paginate(page, per_page=pagerows)
    return render_template('fee345/fee4_search_audit.html', pagination=pagination,page=page)