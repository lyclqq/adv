# -*- coding: utf-8 -*-

from flask import Blueprint,render_template,current_app,url_for,redirect,session,request,flash,g
import json
import os
from functools import wraps
from app.common import is_login,ins_logs,month_difference,get_month
from app import db
from app.view import search_orders
from app.models.contract import Customers,Orders
from app.models.other import Files
from app.models.bill import Wordnumbers,Fee1
from app.forms.customer import CustomerForm
from app.forms.order import OrderForm,OrderSearchForm,OrderupfileForm
from app.forms.fee import FeeSearchForm
import datetime

orderauditView=Blueprint('order_audit',__name__)


#客户管理
@orderauditView.route('/customer_search',methods=["GET","POST"])
@is_login
def customer_search():
    uid = session.get('user_id')
    form=OrderSearchForm()

    page = request.args.get('page', 1, type=int)
    customers=Customers()
    if form.validate_on_submit():
        title=form.title.data
        pagination=customers.search_customers( keywords=title,page=1)
    else:
        pagination=customers.search_customers(None,page=page)

    result=pagination.items
    return render_template('orderaudit/customer_search.html', page=page, pagination=pagination, posts=result,form=form)

#合同管理
@orderauditView.route('/order_search',methods=["GET","POST"])
@is_login
def order_search():
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    form=OrderSearchForm()
    pagination,page=search_orders(searchform=form,page=page)
    result=pagination.items
    return render_template('orderaudit/order_search.html', page=page, pagination=pagination, posts=result,form=form)

#合同审核
@orderauditView.route('/order_audit/<int:oid>/<int:add_id>',methods=["GET","POST"])
@orderauditView.route('/order_audit/<int:oid>',methods=["GET","POST"])
@is_login
def order_audit(oid,add_id=0):
    uid = session.get('user_id')
    form=OrderSearchForm()
    if  add_id>0:
        order = Orders.query.filter(Orders.id > oid,Orders.status=='待审').first_or_404()
        oid=order.id
    else:
        order=Orders.query.filter(Orders.id==oid).first_or_404()
    orderfiles=Files.query.filter(Files.order_id==oid).all()
    if form.validate_on_submit():
        try:

            if order.status=='待审' and ( form.status.data=='作废' or form.status.data=='未审'):
                order.status = form.status.data
                order.update_datetime=datetime.datetime.now()
                order.cuser_id = uid
                db.session.add(order)
            elif order.status=='待审' and form.status.data=='己审' :
                order.status = form.status.data
                order.update_datetime = datetime.datetime.now()
                order.cuser_id=uid
                systemtoday = get_month()
                if month_difference(systemtoday,order.contract_date)==0:#当月
                    order.Fee12=order.Fee11
                if systemtoday.year==order.contract_date.year: #当年
                    order.Fee13 = order.Fee11
                db.session.add(order)
                customer = Customers.query.filter(Customers.id == order.cutomer_id).first_or_404()
                customer.status = 'on'
                db.session.add(customer)
                wordnumber=Wordnumbers()
                wordnumber.order_id=oid
                wordnumber.feedate=order.contract_date
                wordnumber.type='order'
                wordnumber.wordnumber=order.wordnumber
                wordnumber.status='on'
                wordnumber.iuser_id=order.iuser_id
                wordnumber.cuser_id=uid
                db.session.add(wordnumber)
                fee1=Fee1()
                fee1.order_id=oid
                fee1.feedate=order.contract_date
                fee1.fee=order.Fee11
                fee1.iuser_id=order.iuser_id
                fee1.cuser_id=uid
                fee1.status='on'
                db.session.add(fee1)
            elif order.status=='己审' and form.status.data=='完成':
                order.status = form.status.data
                order.update_datetime = datetime.datetime.now()
                systemtoday = get_month(lastday=True)
                order.end_date=systemtoday #完成日期为系统当月最后一天
                db.session.add(order)
                db.session.commit()
            flash('操作完成.', 'success')
            ins_logs(uid, '合同状态变更,id=' + str(oid), type='order_audit')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            flash('审核失败')
    form.status.data = order.status
    return render_template('orderaudit/order_audit.html', order=order,posts=orderfiles,form=form)

#合同修改
@orderauditView.route('/order_edit/<int:oid>',methods=["GET","POST"])
@is_login
def order_edit(oid):
    uid = session.get('user_id')
    order=Orders.query.filter(Orders.id==oid).first_or_404()
    form=OrderForm()
    form.customername.data = '1111'  # 只是为了验证加上
    if form.validate_on_submit():
        try:
            if order.status=="己审":
                order.title=form.title.data
                order.ordernumber=form.ordernumber.data
                order.update_datetime=datetime.datetime.now()
                db.session.add(order)
                db.session.commit()
                ins_logs(uid, '修改合同，orderid='+str(oid), type='order_audit')
                flash("修改成功")
            else:
                flash("不是己审状态，不能修改")
        except Exception as e:
            current_app.logger.error(e)
            flash('修改失败')
    else:
        form.notes.data=order.notes
        form.notes.render_kw = {'class': 'form-control', 'readonly': True}
        form.title.data=order.title
        form.ordernumber.data=order.ordernumber
        form.contract_date.data=order.contract_date
        form.contract_date.render_kw = {'class': 'form-control', 'readonly': True}
        form.name.data=order.name
        form.name.render_kw = {'class': 'form-control', 'readonly': True}
        form.fee1.data=order.Fee11
        form.fee1.render_kw = {'class': 'form-control', 'readonly': True}
        form.words.data=order.wordnumber
        form.words.render_kw = {'class': 'form-control', 'readonly': True}
        if order.status == "己审" :
            form.submit.render_kw = {'class': 'form-control', 'disabled': False}
        else:
            form.submit.render_kw = {'class': 'form-control', 'disabled': True}
    return render_template('contract/order_edit.html',form=form)

#附件审核
@orderauditView.route('/files_list/<int:oid>')
@is_login
def files_list(oid):
    uid = session.get('user_id')
    order=Orders.query.filter(Orders.id==oid).first_or_404()
    orderfiles=Files.query.filter(Files.order_id==oid).all()
    return render_template('orderaudit/files_list.html', order=order,posts=orderfiles)

#附件状态
@orderauditView.route('/file_status/<int:fid>')
@is_login
def file_status(fid):
    uid=session.get('user_id')
    try:
        files = Files.query.filter_by(id=fid).first_or_404()
        if files.status=='on':
            files.status='off'
        elif files.status=='stay':
            files.status='on'
        else:
            files.status='stay'
        db.session.commit()
        flash('修改成功.', 'success')
        ins_logs(uid,'修改附件状态,orderid='+str(files.order_id)+',id='+str(fid),type='order_audit')
    except Exception as e:
        current_app.logger.error(e)
        flash('修改失败')
    return redirect(url_for('order_audit.files_list',oid=files.order_id))

#附件状态
@orderauditView.route('/customer_status/<int:cuid>')
@is_login
def customer_status(cuid):
    uid=session.get('user_id')
    page = request.args.get('page', 1, type=int)
    try:
        customer = Customers.query.filter_by(id=cuid).first_or_404()
        if customer.status=='on':
            customer.status='off'
        elif customer.status=='stay':
            customer.status='on'
        else:
            customer.status='stay'
        db.session.commit()
        ins_logs(uid,'修改客户状态,id='+str(cuid),type='order_audit')
    except Exception as e:
        current_app.logger.error(e)
        flash('修改失败')
    return redirect(url_for('order_audit.customer_search',page=page))

#删除附件
@orderauditView.route('/file_del/<int:fid>')
@is_login
def file_del(fid):
    uid=session.get('user_id')
    try:
        files = Files.query.filter_by(id=fid).first_or_404()
        ins_logs(uid, '删除附件,orderid=' + str(files.order_id) + ',id=' + str(fid), type='order_audit')
        db.session.delete(files)
        db.session.commit()
        flash('删除成功.', 'success')
    except Exception as e:
        current_app.logger.error(e)
        flash('删除失败')
    return redirect(url_for('order_audit.files_list',oid=files.order_id))

#客户查看
@orderauditView.route('/customer_show/<int:cuid>')
@is_login
def customer_show(cuid):
    uid = session.get('user_id')
    customer=Customers.query.filter(Customers.id==cuid).first_or_404()
    orderlist=Orders.query.filter(Orders.cutomer_id==cuid).all()
    return render_template('orderaudit/customer_show.html', customer=customer,posts=orderlist)

#合同审核页
@orderauditView.route('/fee1_audit/<int:oid>')
@is_login
def fee1_audit(oid):
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    pagerows = current_app.config['PAGEROWS']
    order = Orders.query.filter(Orders.id == oid).first_or_404()
    pagination = Fee1.query.filter(Fee1.order_id==oid).order_by(Fee1.id.desc()).paginate(page, per_page=pagerows)
    return render_template('orderaudit/fee1_audit.html', order=order,page=page,pagination=pagination)

#合同金额审核同意
@orderauditView.route('/fee1_audit_on/<int:oid>/<int:fid>')
@is_login
def fee1_audit_on(oid,fid):
    uid = session.get('user_id')
    fee1=Fee1.query.filter(Fee1.id==fid).first_or_404()
    order = Orders.query.filter(Orders.id == oid).first_or_404()
    total=order.Fee11+fee1.fee
    if fee1.status=='stay' and total>=0:
        try:
            order.update_datetime=datetime.datetime.now()
            order.Fee11=total
            systemtoday = get_month()
            if month_difference(systemtoday, order.contract_date) == 0:  # 当月
                order.Fee12 = order.Fee12+fee1.fee
            if systemtoday.year == order.contract_date.year:  # 当年
                order.Fee13 = order.Fee13+fee1.fee
            db.session.add(order)
            fee1.status='on'
            fee1.cuser_id=uid
            db.session.add(fee1)
            db.session.commit()
            ins_logs(uid, '审核合同金额同意，orderid=' + oid, type='orderaudit')
        except Exception as e:
            current_app.logger.error(e)
            flash('提交失败')
    else:
        flash('不符合条件！')
    return redirect(url_for('order_audit.fee1_audit',oid=oid))

#合同金额审核不同意
@orderauditView.route('/fee1_audit_off/<int:oid>/<int:fid>')
@is_login
def fee1_audit_off(oid,fid):
    uid = session.get('user_id')
    fee1=Fee1.query.filter(Fee1.id==fid).first_or_404()
    if fee1.status=='stay' :
        try:
            fee1.status='off'
            fee1.cuser_id=uid
            db.session.commit()
            ins_logs(uid, '审核合同金额不同意，orderid=' + oid, type='orderaudit')
        except Exception as e:
            current_app.logger.error(e)
            flash('提交失败')
    else:
        flash('不符合条件！')
    return redirect(url_for('order_audit.fee1_audit',oid=oid))

#合同金额审核查询页
@orderauditView.route('/fee1_search_audit',methods=["GET","POST"])
@is_login
def fee1_search_audit():
    uid = session.get('user_id')
    form = FeeSearchForm()
    pagerows = current_app.config['PAGEROWS']
    if form.validate_on_submit():
        page = 1
        session['fee1_status'] = form.status.data
        fee_status = form.status.data
    else:
        page = request.args.get('page', 1, type=int)
        if session.get('fee1_status') is None:
            fee_status = 'all'
        else:
            fee_status = session.get('fee1_status')
            form.status.data = fee_status
    if fee_status == 'all':
        pagination = Fee1.query.order_by(Fee1.id.desc()).paginate(page, per_page=pagerows)
    else:
        pagination = Fee1.query.filter(Fee1.status == fee_status).order_by(Fee1.id.desc()).paginate(page, per_page=pagerows)
    return render_template('orderaudit/fee1_search_audit.html', pagination=pagination,page=page,form=form)

