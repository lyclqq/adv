# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, current_app, url_for, redirect, session, request, flash, g
import json
import os
from functools import wraps
from app.common import is_login, ins_logs,month_difference
from app import db
from app.models.contract import Customers, Orders
from app.view import search_orders
from app.models.system import Systeminfo
from app.models.bill import Wordnumbers, Fee1, Fee2, Fee3, Fee4, Fee5
from app.forms.customer import CustomerForm
from app.forms.fee import Fee2Form, AuditForm, Fee3Form,Fee5Form,FeeSearchForm
from app.forms.order import OrderForm, OrderSearchForm, OrderupfileForm
import datetime

fee5View = Blueprint('fee5', __name__)

# 合同查询为管理
@fee5View.route('/order_search_admin', methods=["GET", "POST"])
@is_login
def order_search_admin():
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    form=OrderSearchForm()
    pagination,page=search_orders(searchform=form,page=page)
    result = pagination.items
    return render_template('fee5/order_search_admin.html', page=page, pagination=pagination, posts=result, form=form)

# 绩效金额输入
@fee5View.route('/fee5_input/<int:oid>', methods=["GET", "POST"])
@is_login
def fee5_input(oid):
    uid = session.get('user_id')
    form = Fee5Form()
    form.scale.data= get_scale()

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
                fee2_sum=0
                fee5 = Fee5()
                fee5.order_id = oid
                fee5.status = 'stay'
                fee5.iuser_id = uid
                db.session.add(fee5)
                for item in request.form:
                    if item[:5]=='Fee2_':
                        str_fee2id=item[5:]
                        fee2=Fee2.query.filter(Fee2.id==str_fee2id).first()
                        if fee2 is not None and fee2.status=='on' and fee2.fee5_id==0:
                            fee2_sum=fee2_sum+fee2.fee
                            fee2.fee5_id=fee5.id
                            db.session.add(fee2)
                fee5.feedate = form.fee_date.data
                fee5.fee = fee2_sum
                fee5.scale = form.scale.data
                fee5.prize = form.prize.data
                fee5.notes = form.notes.data
                db.session.add(fee5)
                db.session.commit()
                flash('录入成功.', 'success')
                ins_logs(uid, '绩效金额录入,id=' + str(oid), type='fee5')

        except Exception as e:
            current_app.logger.error(e)
            flash('录入失败')

    result_fee2 = Fee2.query.filter(Fee2.order_id == oid,Fee2.status=='on',Fee2.fee5_id==0).all()
    result_fee5=Fee5.query.filter(Fee5.order_id==oid).order_by(Fee5.id.desc()).all()
    return render_template('fee5/fee5_input.html', form=form, order=order, result_fee2=result_fee2,result_fee5=result_fee5)

#绩效金额列表
@fee5View.route('/fee5_search_admin', methods=["GET", "POST"])
@is_login
def fee5_search_admin():
    uid = session.get('user_id')
    form = FeeSearchForm()
    pagerows = current_app.config['PAGEROWS']
    if form.validate_on_submit():
        page = 1
        session['fee5_status'] = form.status.data
        fee_status = form.status.data
    else:
        page = request.args.get('page', 1, type=int)
        if session.get('fee5_status') is None:
            fee_status = 'all'
        else:
            fee_status = session.get('fee5_status')
            form.status.data = fee_status
    if fee_status == 'all':
        pagination = Fee5.query.order_by(Fee5.id.desc()).paginate(page, per_page=pagerows)
    else:
        pagination = Fee5.query.filter(Fee5.status == fee_status).order_by(Fee5.id.desc()).paginate(page,
                                                                                                    per_page=pagerows)
    return render_template('fee5/fee5_search_admin.html', pagination=pagination,page=page,form=form)

# 合同查询为审核
@fee5View.route('/order_search_audit', methods=["GET", "POST"])
@is_login
def order_search_audit():
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    form=OrderSearchForm()
    pagination,page=search_orders(searchform=form,page=page)
    result = pagination.items
    return render_template('fee5/order_search_audit.html', page=page, pagination=pagination, posts=result, form=form)


#发票审核页
@fee5View.route('/fee5_audit/<int:oid>')
@is_login
def fee5_audit(oid):
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    pagerows = current_app.config['PAGEROWS']
    order = Orders.query.filter(Orders.id == oid).first_or_404()
    pagination = Fee5.query.filter(Fee5.order_id==oid).order_by(Fee5.id.desc()).paginate(page, per_page=pagerows)
    return render_template('fee5/fee5_audit.html', order=order,page=page,pagination=pagination)

#绩效金额审核同意
@fee5View.route('/fee5_audit_on/<int:oid>/<int:fid>')
@is_login
def fee5_audit_on(oid,fid):
    uid = session.get('user_id')
    fee5=Fee5.query.filter(Fee5.id==fid).first_or_404()
    order = Orders.query.filter(Orders.id == oid).first_or_404()
    total=order.Fee51+fee5.fee
    if fee5.status=='stay' and total>=0:
        try:
            order.update_datetime=datetime.datetime.now()
            order.Fee51=total
            order.Fee52=order.Fee52+fee5.fee
            order.Fee61=order.Fee61+fee5.prize
            db.session.add(order)
            fee5.status='on'
            fee5.cuser_id=uid
            db.session.add(fee5)
            db.session.commit()
            ins_logs(uid, '审核绩效金额同意，orderid=' + str(oid), type='fee5')
        except Exception as e:
            current_app.logger.error(e)
            flash('提交失败')
    else:
        flash('不符合条件！')
    return redirect(url_for('fee5.fee5_audit_show',oid=oid,fid=fid))

#绩效金额审核拒绝
@fee5View.route('/fee5_audit_off/<int:oid>/<int:fid>')
@is_login
def fee5_audit_off(oid,fid):
    uid = session.get('user_id')
    fee5=Fee5.query.filter(Fee5.id==fid).first_or_404()
    if fee5.status=='stay' :
        try:
            fee5.status='off'
            fee5.cuser_id=uid
            db.session.add(fee5)
            Fee2.query.filter(Fee2.fee5_id >= fid).update({"fee5_id": 0}, synchronize_session=False)
            db.session.commit()
            ins_logs(uid, '审核绩效金额拒绝，fee5id=' + str(fid)+',orderid='+str(oid), type='fee5')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            flash('提交失败')
    else:
        flash('不符合条件！')
    return redirect(url_for('fee5.fee5_audit_show',oid=oid,fid=fid))

#到帐金额查询
@fee5View.route('/fee5_search_audit', methods=["GET", "POST"])
@is_login
def fee5_search_audit():
    uid = session.get('user_id')
    form = FeeSearchForm()
    pagerows = current_app.config['PAGEROWS']
    if form.validate_on_submit():
        page = 1
        session['fee5_status'] = form.status.data
        fee_status = form.status.data
    else:
        page = request.args.get('page', 1, type=int)
        if session.get('fee5_status') is None:
            fee_status = 'all'
        else:
            fee_status = session.get('fee5_status')
            form.status.data = fee_status
    if fee_status == 'all':
        pagination = Fee5.query.order_by(Fee5.id.desc()).paginate(page, per_page=pagerows)
    else:
        pagination = Fee5.query.filter( Fee5.status == fee_status).order_by(Fee5.id.desc()).paginate(page,
                                     per_page=pagerows)
    return render_template('fee5/fee5_search_audit.html', pagination=pagination,page=page,form=form)

#绩效金额审核详情
@fee5View.route('/fee5_audit_show/<int:oid>/<int:fid>')
@is_login
def fee5_audit_show(oid,fid):
    uid = session.get('user_id')
    order = Orders.query.filter(Orders.id == oid).first_or_404()
    fee5=Fee5.query.filter(Fee5.id==fid).first_or_404()
    fee2=Fee2.query.filter(Fee2.fee5_id==fid).all()
    return render_template('fee5/fee5_audit_show.html', order=order,fee5=fee5,fee2=fee2)
#读取税率
def get_scale():
    systeminfo=Systeminfo.query.filter(Systeminfo.id==1).first()
    return systeminfo.propor

# 刊登金额查看
@fee5View.route('/fee5_show/<int:oid>', methods=["GET", "POST"])
@is_login
def fee5_show(oid):
    uid = session.get('user_id')
    form=FeeSearchForm()
    pagerows = current_app.config['PAGEROWS']

    order = Orders.query.filter(Orders.id == oid).first_or_404()
    if form.validate_on_submit():
        page=1
        session['fee5_status']=form.status.data
        fee_status=form.status.data
    else:
        page = request.args.get('page', 1, type=int)
        if session.get('fee5_status') is None:
            fee_status='all'
        else:
            fee_status = session.get('fee5_status')
            form.status.data = fee_status
    if fee_status=='all':
        pagination = Fee5.query.filter(Fee5.order_id == oid).order_by(Fee5.id.desc()).paginate(page, per_page=pagerows)
    else:
        pagination = Fee5.query.filter(Fee5.order_id == oid,Fee5.status==fee_status).order_by(Fee5.id.desc()).paginate(page,
                                                                                                   per_page=pagerows)
    return render_template('fee5/fee5_show.html', order=order, pagination=pagination,page=page,form=form)