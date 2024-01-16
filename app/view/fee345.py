# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, current_app, url_for, redirect, session, request, flash, g
import json
import os
from functools import wraps
from app.common import is_login, ins_logs,month_difference,get_month
from app import db
from app.view import search_orders
from app.models.contract import Customers, Orders
from app.models.system import Systeminfo
from app.models.bill import Wordnumbers, Fee1, Fee2, Fee3, Fee4, Fee5
from app.forms.customer import CustomerForm
from app.forms.fee import Fee2Form, AuditForm, Fee3Form,FeeSearchForm
from app.forms.order import OrderForm, OrderSearchForm, OrderupfileForm
import datetime

fee345View = Blueprint('fee345', __name__)


# 合同查询为管理
@fee345View.route('/order_search_admin', methods=["GET", "POST"])
@is_login
def order_search_admin():
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    form=OrderSearchForm()
    pagination,page=search_orders(searchform=form,page=page)
    result = pagination.items
    return render_template('fee345/order_search_admin.html', page=page, pagination=pagination, posts=result, form=form)

# 合同查询为审核
@fee345View.route('/order_search_audit', methods=["GET", "POST"])
@is_login
def order_search_audit():
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    form=OrderSearchForm()
    pagination,page=search_orders(searchform=form,page=page)
    result = pagination.items
    return render_template('fee345/order_search_audit.html', page=page, pagination=pagination, posts=result, form=form)


# 到帐金额输入
@fee345View.route('/fee4_input/<int:oid>', methods=["GET", "POST"])
@is_login
def fee4_input(oid):
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    form = Fee3Form()
    order = Orders.query.filter(Orders.id == oid).first_or_404()
    if order.status != '己审' and order.status!='完成':
        form.submit.render_kw={'class':'form-control','disabled':'true'}
    else:
        form.submit.render_kw = {'class': 'form-control'}
    if form.validate_on_submit():
        try:
            systeminfo = Systeminfo.query.filter(Systeminfo.id == 1).first()
            if month_difference(systeminfo.systemmonth, form.fee_date.data) >= 1:
                flash('不能晚于系统当月！.', 'success')
            else:
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
    if order.status != '己审' and order.status!='完成':
        form.submit.render_kw={'class':'form-control','disabled':'true'}
    else:
        form.submit.render_kw = {'class': 'form-control'}
    if form.validate_on_submit():
        try:
            systeminfo = Systeminfo.query.filter(Systeminfo.id == 1).first()
            if month_difference(systeminfo.systemmonth, form.fee_date.data) >= 1:
                flash('不能晚于系统当月！.', 'success')
            else:
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

#发票查询
@fee345View.route('/fee3_search_audit')
@is_login
def fee3_search_audit():
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    pagerows = current_app.config['PAGEROWS']
    pagination = Fee3.query.order_by(Fee3.id.desc()).paginate(page, per_page=pagerows)
    return render_template('fee345/fee3_search_audit.html', pagination=pagination,page=page)

#到帐金额查询
@fee345View.route('/fee4_search_audit')
@is_login
def fee4_search_audit():
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    pagerows = current_app.config['PAGEROWS']
    pagination = Fee4.query.order_by(Fee4.id.desc()).paginate(page, per_page=pagerows)
    return render_template('fee345/fee4_search_audit.html', pagination=pagination,page=page)


#发票审核页
@fee345View.route('/fee3_audit/<int:oid>')
@is_login
def fee3_audit(oid):
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    pagerows = current_app.config['PAGEROWS']
    order = Orders.query.filter(Orders.id == oid).first_or_404()
    pagination = Fee3.query.filter(Fee3.order_id==oid).order_by(Fee3.id.desc()).paginate(page, per_page=pagerows)
    return render_template('fee345/fee3_audit.html', order=order,page=page,pagination=pagination)

#到帐审核页
@fee345View.route('/fee4_audit/<int:oid>')
@is_login
def fee4_audit(oid):
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    pagerows = current_app.config['PAGEROWS']
    order = Orders.query.filter(Orders.id == oid).first_or_404()
    pagination = Fee4.query.filter(Fee4.order_id==oid).order_by(Fee4.id.desc()).paginate(page, per_page=pagerows)
    return render_template('fee345/fee4_audit.html', order=order,page=page,pagination=pagination)

#发票金额审核同意
@fee345View.route('/fee3_audit_on/<int:oid>/<int:fid>')
@is_login
def fee3_audit_on(oid,fid):
    uid = session.get('user_id')
    fee3=Fee3.query.filter(Fee3.id==fid).first_or_404()
    order = Orders.query.filter(Orders.id == oid).first_or_404()
    total=order.Fee31+fee3.fee
    if fee3.status=='stay' and total>=0 and order.Fee11>=total:
        try:
            order.update_datetime=datetime.datetime.now()
            systemtoday=get_month()
            if month_difference(systemtoday,fee3.feedate)==0:#当月
                order.Fee32=order.Fee32+fee3.fee
            if systemtoday.year==fee3.feedate.year: #当年
                order.Fee33 = order.Fee33 + fee3.fee
            order.Fee31=total
            db.session.add(order)
            fee3.status='on'
            fee3.cuser_id=uid
            db.session.commit()
            ins_logs(uid, '审核发票金额同意，orderid=' + str(oid), type='fee345')
        except Exception as e:
            current_app.logger.error(e)
            flash('提交失败')
    else:
        flash('不符合条件！')
    return redirect(url_for('fee345.fee3_audit',oid=oid,fid=fid))

#发票金额审核拒绝
@fee345View.route('/fee3_audit_off/<int:oid>/<int:fid>')
@is_login
def fee3_audit_off(oid,fid):
    uid = session.get('user_id')
    fee3=Fee3.query.filter(Fee3.id==fid).first_or_404()
    if fee3.status=='stay' :
        try:
            fee3.status='off'
            fee3.cuser_id=uid
            db.session.commit()
            ins_logs(uid, '审核发票金额拒绝，fee3id=' + str(fid), type='fee345')
        except Exception as e:
            current_app.logger.error(e)
            flash('提交失败')
    else:
        flash('不符合条件！')
    return redirect(url_for('fee345.fee3_audit',oid=oid,fid=fid))

#到帐金额审核同意
@fee345View.route('/fee4_audit_on/<int:oid>/<int:fid>')
@is_login
def fee4_audit_on(oid,fid):
    uid = session.get('user_id')
    fee4=Fee4.query.filter(Fee4.id==fid).first_or_404()
    order = Orders.query.filter(Orders.id == oid).first_or_404()
    total=order.Fee41+fee4.fee
    if fee4.status=='stay' and total>=0 and order.Fee11>=total:
        try:
            order.update_datetime=datetime.datetime.now()
            order.Fee41=total
            systemtoday=get_month()
            if month_difference(systemtoday,fee4.feedate)==0:#当月
                order.Fee42=order.Fee42+fee4.fee
            if systemtoday.year==fee4.feedate.year: #当年
                order.Fee43 = order.Fee43 + fee4.fee
            db.session.add(order)
            fee4.status='on'
            fee4.cuser_id=uid
            db.session.commit()
            ins_logs(uid, '审核到帐金额同意，orderid=' + str(oid), type='fee345')
        except Exception as e:
            current_app.logger.error(e)
            flash('提交失败')
    else:
        flash('不符合条件！')
    return redirect(url_for('fee345.fee4_audit',oid=oid,fid=fid))

#到帐金额审核拒绝
@fee345View.route('/fee4_audit_off/<int:oid>/<int:fid>')
@is_login
def fee4_audit_off(oid,fid):
    uid = session.get('user_id')
    fee4=Fee4.query.filter(Fee4.id==fid).first_or_404()
    if fee4.status=='stay' :
        try:
            fee4.status='off'
            fee4.cuser_id=uid
            db.session.commit()
            ins_logs(uid, '审核到帐金额拒绝，fee4id=' + str(fid), type='fee345')
        except Exception as e:
            current_app.logger.error(e)
            flash('提交失败')
    else:
        flash('不符合条件！')
    return redirect(url_for('fee345.fee4_audit',oid=oid,fid=fid))

# 发票金额查看
@fee345View.route('/fee3_show/<int:oid>', methods=["GET", "POST"])
@is_login
def fee3_show(oid):
    uid = session.get('user_id')
    form=FeeSearchForm()
    pagerows = current_app.config['PAGEROWS']

    order = Orders.query.filter(Orders.id == oid).first_or_404()
    if form.validate_on_submit():
        page=1
        session['fee3_status']=form.status.data
        fee_status=form.status.data
    else:
        page = request.args.get('page', 1, type=int)
        if session.get('fee3_status') is None:
            fee_status='all'
        else:
            fee_status = session.get('fee3_status')
            form.status.data = fee_status
    if fee_status=='all':
        pagination = Fee3.query.filter(Fee3.order_id == oid).order_by(Fee3.id.desc()).paginate(page, per_page=pagerows)
    else:
        pagination = Fee3.query.filter(Fee3.order_id == oid,Fee3.status==fee_status).order_by(Fee3.id.desc()).paginate(page,
                                                                                                   per_page=pagerows)
    return render_template('fee345/fee3_show.html', order=order, pagination=pagination,page=page,form=form)

# 到帐金额查看
@fee345View.route('/fee4_show/<int:oid>', methods=["GET", "POST"])
@is_login
def fee4_show(oid):
    uid = session.get('user_id')
    form=FeeSearchForm()
    pagerows = current_app.config['PAGEROWS']
    order = Orders.query.filter(Orders.id == oid).first_or_404()
    if form.validate_on_submit():
        page=1
        session['fee4_status']=form.status.data
        fee_status=form.status.data
    else:
        page = request.args.get('page', 1, type=int)
        if session.get('fee4_status') is None:
            fee_status='all'
        else:
            fee_status = session.get('fee4_status')
            form.status.data = fee_status
    if fee_status=='all':
        pagination = Fee4.query.filter(Fee4.order_id == oid).order_by(Fee4.id.desc()).paginate(page, per_page=pagerows)
    else:
        pagination = Fee4.query.filter(Fee4.order_id == oid,Fee4.status==fee_status).order_by(Fee4.id.desc()).paginate(page,
                                                                                                   per_page=pagerows)
    return render_template('fee345/fee4_show.html', order=order, pagination=pagination,page=page,form=form)