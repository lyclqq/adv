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
    user=Users.query.get(1)
    result=user.search_articles('社务',page=1)
    #current_app.logger.error('pages is '+str(result['pages']))
    return render_template('admin/index.html')