# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, current_app, url_for, redirect, session, request, flash, g
import json
import os
from functools import wraps
from app.common import is_login, ins_logs, month_difference, get_month
from app import db
from app.models.contract import Customers, Orders
from app.models.system import Systeminfo
from app.models.bill import Wordnumbers, Fee1, Fee2
from app.forms.customer import CustomerForm
from app.forms.fee import Fee2Form, AuditForm, FeeSearchForm
from app.forms.order import OrderForm, OrderSearchForm, OrderupfileForm
from app.view import search_orders
import datetime

fee2View = Blueprint('fee2', __name__)


# 合同查询为管理
@fee2View.route('/order_search_admin', methods=["GET", "POST"])
@is_login
def order_search_admin():
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    form = OrderSearchForm()
    pagination, page = search_orders(searchform=form, page=page)
    result = pagination.items
    return render_template('fee2/order_search_admin.html', page=page, pagination=pagination, posts=result, form=form)


# 刊登金额输入
@fee2View.route('/fee2_input/<int:oid>', methods=["GET", "POST"])
@is_login
def fee2_input(oid):
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    form = Fee2Form()
    order = Orders.query.filter(Orders.id == oid).first_or_404()
    if order.status != '己审' and order.status != '完成':
        form.submit.render_kw = {'class': 'form-control', 'disabled': 'true'}
    else:
        form.submit.render_kw = {'class': 'form-control'}
    if form.validate_on_submit():
        try:
            systeminfo = Systeminfo.query.filter(Systeminfo.id == 1).first()
            if month_difference(systeminfo.systemmonth, form.fee_date.data) >= 1:
                flash('不能晚于系统当月！.', 'success')
            else:
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

                    db.session.add(fee2)
                    db.session.commit()
                    flash('录入成功.', 'success')
                    ins_logs(uid, '刊登金额录入,orderid=' + str(oid), type='fee2')

                else:
                    flash('余额不能小于0!')
        except Exception as e:
            current_app.logger.error(e)
            flash('录入失败')
    pagination = Fee2.query.filter(Fee2.order_id == oid).order_by(Fee2.id.desc()).paginate(page, per_page=8)
    return render_template('fee2/fee2_input.html', form=form, order=order, pagination=pagination, page=page)


@fee2View.route('/fee2_search_admin', methods=["GET", "POST"])
@is_login
def fee2_search_admin():
    uid = session.get('user_id')
    form = FeeSearchForm()
    pagerows = current_app.config['PAGEROWS']
    if form.validate_on_submit():

        page = 1
        session['fee2_status'] = form.status.data
        fee_status = form.status.data
    else:
        page = request.args.get('page', 1, type=int)
        if session.get('fee2_status') is None:
            fee_status = 'all'
        else:
            fee_status = session.get('fee2_status')
            form.status.data = fee_status
    if fee_status == 'all':
        pagination = Fee2.query.order_by(Fee2.id.desc()).paginate(page, per_page=pagerows)
    else:
        pagination = Fee2.query.filter(Fee2.status == fee_status).order_by(Fee2.id.desc()).paginate(page,
                                                                                                    per_page=pagerows)
    return render_template('fee2/fee2_search_admin.html', pagination=pagination, page=page, form=form)


@fee2View.route('/fee2_search_audit', methods=["GET", "POST"])
@is_login
def fee2_search_audit():
    uid = session.get('user_id')
    form = FeeSearchForm()
    pagerows = current_app.config['PAGEROWS']
    if form.validate_on_submit():
        page = 1
        session['fee2_status'] = form.status.data
        fee_status = form.status.data
    else:
        page = request.args.get('page', 1, type=int)
        if session.get('fee2_status') is None:
            fee_status = 'all'
        else:
            fee_status = session.get('fee2_status')
            form.status.data = fee_status
    if fee_status == 'all':
        pagination = Fee2.query.order_by(Fee2.id.desc()).paginate(page, per_page=pagerows)
    else:
        pagination = Fee2.query.filter(Fee2.status == fee_status).order_by(Fee2.id.desc()).paginate(page,
                                                                                                    per_page=pagerows)
    return render_template('fee2/fee2_search_udit.html', pagination=pagination, page=page, form=form)


# 刊登金额审核
@fee2View.route('/fee2_audit/<int:oid>')
@is_login
def fee2_audit(oid):
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    pagerows = current_app.config['PAGEROWS']
    order = Orders.query.filter(Orders.id == oid).first_or_404()
    pagination = Fee2.query.filter(Fee2.order_id == oid).order_by(Fee2.id.desc()).paginate(page, per_page=pagerows)
    return render_template('fee2/fee2_audit.html', order=order, page=page, pagination=pagination)


# 合同查询为管理
@fee2View.route('/order_search_audit', methods=["GET", "POST"])
@is_login
def order_search_audit():
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    form = OrderSearchForm()
    pagination, page = search_orders(searchform=form, page=page)
    result = pagination.items
    return render_template('fee2/order_search_audit.html', page=page, pagination=pagination, posts=result, form=form)


# 刊登金额审核同意，内页
@fee2View.route('/fee2_audit_on/<int:oid>/<int:fid>')
@is_login
def fee2_audit_on(oid, fid):
    result=fee2_audit_ok(oid,fid)
    if result.get("tf")==True:
        flash("成功！")
    else:
        flash(result.get("info"))
    return redirect(url_for('fee2.fee2_audit', oid=oid, fid=fid))

# 刊登金额审核同意，外页
@fee2View.route('/fee2_audit_out_on/<int:oid>/<int:fid>/<int:page>')
@is_login
def fee2_audit_out_on(oid, fid,page):
    result=fee2_audit_ok(oid,fid)
    if result.get("tf")==True:
        flash("成功！")
    else:
        flash(result.get("info"))
    return redirect(url_for('fee2.fee2_search_audit',page=page))

#fee2审核同意
def fee2_audit_ok(oid,fid):
    result={}
    uid = session.get('user_id')
    fee2 = Fee2.query.filter(Fee2.id == fid).first_or_404()
    order = Orders.query.filter(Orders.id == oid).first_or_404()
    total = order.Fee21 + fee2.fee
    if fee2.status == 'stay' and total >= 0 and order.Fee11 >= total:
        try:
            order.update_datetime = datetime.datetime.now()
            order.Fee21 = total
            systemtoday = get_month()
            if month_difference(systemtoday, fee2.feedate) == 0:  # 当月
                order.Fee22 = order.Fee22 + fee2.fee
            if systemtoday.year == fee2.feedate.year:  # 当年
                order.Fee23 = order.Fee23 + fee2.fee
            order.area = order.area + fee2.area
            db.session.add(order)
            fee2.status = 'on'
            fee2.cuser_id = uid
            db.session.commit()
            ins_logs(uid, '审核刊登金额同意，orderid=' + str(oid), type='fee2')
            result.update({"tf":True})
        except Exception as e:
            current_app.logger.error(e)
            result.update({"tf": False})
            result.update({"info":"提交失败"})
    else:
        result.update({"info":"不符合条件！"})
        result.update({"tf": False})
    return result

# 刊登金额审核拒绝
@fee2View.route('/fee2_audit_off/<int:oid>/<int:fid>')
@is_login
def fee2_audit_off(oid, fid):
    uid = session.get('user_id')
    fee2 = Fee2.query.filter(Fee2.id == fid).first_or_404()
    if fee2.status == 'stay':
        try:
            fee2.status = 'off'
            fee2.cuser_id = uid
            db.session.commit()
            ins_logs(uid, '审核刊登金额拒绝，fee2id=' + str(fid) + '，orderid=' + str(oid), type='fee2')
        except Exception as e:
            current_app.logger.error(e)
            flash('提交失败')
    else:
        flash('不符合条件！')
    return redirect(url_for('fee2.fee2_audit', oid=oid, fid=fid))


# 刊登金额查看
@fee2View.route('/fee2_show/<int:oid>', methods=["GET", "POST"])
@is_login
def fee2_show(oid):
    uid = session.get('user_id')
    form = FeeSearchForm()
    pagerows = current_app.config['PAGEROWS']

    order = Orders.query.filter(Orders.id == oid).first_or_404()
    if form.validate_on_submit():
        page = 1
        session['fee2_status'] = form.status.data
        fee_status = form.status.data
    else:
        page = request.args.get('page', 1, type=int)
        if session.get('fee2_status') is None:
            fee_status = 'all'
        else:
            fee_status = session.get('fee2_status')
            form.status.data = fee_status
    if fee_status == 'all':
        pagination = Fee2.query.filter(Fee2.order_id == oid).order_by(Fee2.id.desc()).paginate(page, per_page=pagerows)
    else:
        pagination = Fee2.query.filter(Fee2.order_id == oid, Fee2.status == fee_status).order_by(
            Fee2.id.desc()).paginate(page,
                                     per_page=pagerows)
    return render_template('fee2/fee2_show.html', order=order, pagination=pagination, page=page, form=form)
