# -*- coding: utf-8 -*-

from flask import Blueprint,render_template,current_app,url_for,redirect,session,request,flash,g
import json
import os
from functools import wraps
from app.common import is_login,ins_logs
from app import db
from sqlalchemy import or_, and_, not_
from app.models.contract import Customers,Orders


contractView=Blueprint('contract_admin',__name__)


#客户管理
@contractView.route('/customer_admin',endpoint='customer_admin')
@is_login
def customer_admin():
    uid = session.get('user_id')
    customers=Customers()
    page = request.args.get('page', 1, type=int)
    pagination = customers.query.filter(Customers.status!='del').order_by(Customers.create_datetime.desc()).paginate(
        page, per_page=current_app.config['PAGEROWS'])

    result = pagination.items
    return render_template('contract/customer_admin.html', page=page, pagination=pagination, posts=result)


#客户删除
@contractView.route('/customer_delete/<int:cuid>')
@is_login
def customer_delete(cuid):
    uid=session.get('user_id')
    try:
        customer = Customers.query.filter_by(id=cuid).first()
        db.session.delete(customer)
        db.session.commit()
        flash('删除成功.', 'success')
        ins_logs(uid,'删除客户'+str(cuid),type='contract')
    except Exception as e:
        current_app.logger.error(e)
        flash('删除失败')
    return redirect(url_for('contract/customer_admin'))

#客户状态
@contractView.route('/customer_status/<int:cuid>')
@is_login
def customer_status(cuid):
    uid=session.get('user_id')
    try:
        customer = Customers.query.filter_by(id=cuid).first()
        db.session.delete(customer)
        db.session.commit()
        flash('删除成功.', 'success')
        ins_logs(uid,'删除客户'+str(cuid),type='contract')
    except Exception as e:
        current_app.logger.error(e)
        flash('删除失败')
    return redirect(url_for('contract/customer_admin'))

#客户修改
@contractView.route('/customer_edit/<int:cuid>')
@is_login
def customer_edit(cuid):
    uid=session.get('user_id')
    try:
        customer = Customers.query.filter_by(id=cuid).first()
        db.session.delete(customer)
        db.session.commit()
        flash('删除成功.', 'success')
        ins_logs(uid,'删除客户'+str(cuid),type='contract')
    except Exception as e:
        current_app.logger.error(e)
        flash('删除失败')
    return redirect(url_for('contract/customer_admin'))