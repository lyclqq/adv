# -*- coding: utf-8 -*-

from flask import Blueprint,render_template,current_app,url_for,redirect,session,request,flash,g
import json
import os
from functools import wraps
from app.common import is_login
from app import db
from sqlalchemy import or_, and_, not_
from app.models.contract import Customers,Orders

contractView=Blueprint('contract',__name__)


#客户管理
@contractView.route('/customer_admin',endpoint='customer_admin')
@is_login
def customer_admin():
    uid = session.get('user_id')
    customers=Customers()
    page = request.args.get('page', 1, type=int)
    pagination = customers.query.filter_by(Customers.status!='del').order_by(Customers.create_time.desc()).paginate(
        page, per_page=current_app.config['PAGEROWS'])

    result = pagination.items
    return render_template('contract/contract_admin.html', page=page, pagination=pagination, posts=result)