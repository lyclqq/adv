# -*- coding: utf-8 -*-

from flask import Blueprint,render_template,current_app,url_for,redirect,session,request,flash,g
import json
import os
from functools import wraps
from app.common import is_login,ins_logs
from app import db
from app.models.contract import Customers,Orders
from app.models.other import Files
from app.models.bill import Wordnumbers,Fee1
from app.forms.customer import CustomerForm
from app.forms.order import OrderForm,OrderSearchForm,OrderupfileForm
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
    return render_template('orderaudit/order_search.html', page=page, pagination=pagination, posts=result,form=form)

#合同审核
@orderauditView.route('/order_audit/<int:oid>',methods=["GET","POST"])
@is_login
def order_audit(oid):
    uid = session.get('user_id')
    form=OrderSearchForm()
    order=Orders.query.filter(Orders.id==oid).first_or_404()
    orderfiles=Files.query.filter(Files.order_id==oid).all()
    if form.validate_on_submit():
        if order.status=='待审' and ( form.status.data=='作废' or form.status.data=='未审'):
            order.status = form.status.data
            order.update_datetime=datetime.datetime.now()
            db.session.add(order)
        if order.status=='待审' and form.status.data=='己审' :
            order.status = form.status.data
            order.update_datetime = datetime.datetime.now()
            db.session.add(order)
            #print('customer is '+str(order.cutomer_id))
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
        if order.status=='己审' and form.status.data=='完成':
            order.status = form.status.data
            order.update_datetime = datetime.datetime.now()
            db.session.add(order)
        try:
            db.session.commit()
            flash('审核成功.', 'success')
            ins_logs(uid, '合同审核,id=' + str(oid), type='order_audit')
        except Exception as e:
            current_app.logger.error(e)
            flash('审核失败')
    form.status.data = order.status
    return render_template('orderaudit/order_audit.html', order=order,posts=orderfiles,form=form)

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
        else:
            files.status='on'
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

