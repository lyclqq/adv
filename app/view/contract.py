# -*- coding: utf-8 -*-

from flask import Blueprint,render_template,current_app,url_for,redirect,session,request,flash,g
import json
import os
from functools import wraps
from app.common import is_login,ins_logs
from app import db
from app.models.contract import Customers,Orders
from app.models.other import Files
from app.forms.customer import CustomerForm
from app.forms.order import OrderForm,OrderSearchForm,OrderupfileForm
import datetime

contractView=Blueprint('contract_admin',__name__)

#客户管理
@contractView.route('/customer_admin',endpoint='customer_admin')
@is_login
def customer_admin():
    uid = session.get('user_id')
    customers=Customers()
    page = request.args.get('page', 1, type=int)

    pagination = customers.query.filter(Customers.status!='delete').order_by(Customers.create_datetime.desc()).paginate(
        page, per_page=current_app.config['PAGEROWS'])

    result = pagination.items
    return render_template('contract/customer_admin.html', page=page, pagination=pagination, posts=result)

#合同管理
@contractView.route('/order_admin',methods=["GET","POST"])
@is_login
def order_admin():
    uid = session.get('user_id')
    form=OrderSearchForm()

    page = request.args.get('page', 1, type=int)
    orders=Orders()
    if form.validate_on_submit():
        title=form.title.data
        status=form.status.data
        pagination=orders.search_orders( keywords=title,status=status,page=1)
    else:
        pagination=orders.search_orders(None,page=page)

    pagination=orders.query.paginate(page, per_page=current_app.config['PAGEROWS'])
    result=pagination.items
    return render_template('contract/order_admin.html', page=page, pagination=pagination, posts=result,form=form)


#客户删除
@contractView.route('/customer_delete/<int:cuid>')
@is_login
def customer_delete(cuid):
    uid=session.get('user_id')
    try:
        customer = Customers.query.filter_by(id=cuid).first()
        customer.status='delete'
        db.session.commit()
        flash('删除成功.', 'success')
        ins_logs(uid,'删除客户,id='+str(cuid),type='contract')
    except Exception as e:
        current_app.logger.error(e)
        flash('删除失败')
    return redirect(url_for('contract_admin.customer_admin'))

#客户状态
@contractView.route('/customer_status/<int:cuid>')
@is_login
def customer_status(cuid):
    uid=session.get('user_id')
    try:
        customer = Customers.query.filter_by(id=cuid).first()
        if customer.status=='stay':
            customer.status='on'
        elif customer.status=='on':
            customer.status='off'
        else:
            customer.status='stay'
        db.session.commit()
        flash('修改成功.', 'success')
        ins_logs(uid,'修改客户状态,id='+str(cuid),type='contract')
    except Exception as e:
        current_app.logger.error(e)
        flash('修改失败')
    return redirect(url_for('contract_admin.customer_admin'))

#客户修改
@contractView.route('/customer_edit/<int:cuid>',methods=["GET","POST"])
@is_login
def customer_edit(cuid):
    uid=session.get('user_id')
    customer = Customers.query.get(id == cuid)
    form=CustomerForm()
    if form.validate_on_submit():
        try:

            customer.name=form.typename.data
            customer.notes=form.typecontent.data

            db.session.commit()
            flash('删除成功.', 'success')
            ins_logs(uid,'删除客户'+str(cuid),type='contract')
        except Exception as e:
            current_app.logger.error(e)
            flash('删除失败')
    return redirect(url_for('contract_admin.customer_admin'))

#客户新增
@contractView.route('/customer_create/',methods=["GET","POST"])
@is_login
def customer_create():
    uid=session.get('user_id')
    form=CustomerForm()
    if form.validate_on_submit():
        customer=Customers()
        customer.name=form.name.data
        customer.notes=form.notes.data
        customer.status='stay'
        try:
            db.session.add(customer)
            db.session.commit()
            ins_logs(uid, '新增客户' , type='contract')
            flash('新增成功')
            return redirect(url_for('contract_admin.customer_admin'))
        except Exception as e:
            current_app.logger.error(e)
            flash('新增失败')
    return render_template('contract/customer_create.html',form=form)

#合同新增
@contractView.route('/order_create/<int:cuid>',methods=["GET","POST"])
@is_login
def order_create(cuid):
    uid=session.get('user_id')
    groupid = session.get('group_id')
    customer=Customers.query.get(cuid)
    form=OrderForm()
    form.customername.readonly=True
    form.customername.data=customer.name
    if form.validate_on_submit():
        order=Orders()
        order.name=form.name.data
        order.title=form.title.data
        order.notes=form.notes.data
        order.Fee11=form.fee1.data
        order.iuser_id=uid
        order.contract_date=form.contract_date.data
        order.status='未审'
        order.group_id = groupid
        try:
            db.session.add(order)
            db.session.commit()
            ins_logs(uid, '新增合同' , type='contract')
            flash('新增成功')
            return redirect(url_for('contract_admin.order_admin'))
        except Exception as e:
            current_app.logger.error(e)
            flash('新增失败')
    return render_template('contract/order_create.html',form=form)

#合同新增
@contractView.route('/order_customer_create/',methods=["GET","POST"])
@is_login
def order_customer_create():
    uid=session.get('user_id')
    groupid=session.get('group_id')
    form=OrderForm()
    form.customername.render_kw={'class': 'form-control','readonly':False}
    if form.validate_on_submit():
        try:
            customer=Customers()
            customer.name=form.customername.data
            customer.status='stay'
            db.session.add(customer)
            db.session.commit()
            order=Orders()
            order.name=form.name.data
            order.title=form.title.data
            order.notes=form.notes.data
            order.Fee11=form.fee1.data
            order.iuser_id=uid
            order.contract_date=form.contract_date.data
            order.status='未审'
            order.cutomer_id=customer.id
            order.group_id=groupid
            db.session.add(order)
            db.session.commit()
            ins_logs(uid, '新增合同' , type='contract')
            flash('新增成功')
            return redirect(url_for('contract_admin.order_admin'))
        except Exception as e:
            current_app.logger.error(e)
            flash('新增失败')
    return render_template('contract/order_create.html',form=form)

#合同修改
@contractView.route('/order_edit/<int:oid>',methods=["GET","POST"])
@is_login
def order_edit(cuid):
    pass

#合同查看
@contractView.route('/order_show/<int:oid>',methods=["GET","POST"])
@is_login
def order_show(oid):
    uid = session.get('user_id')
    order=Orders.query.filter(Orders.id==oid).first()
    if order is None:
        flash('读取合同错误!')
    else:
        orderfiles=Files.query.filter(Files.order_id==oid).all()
        return render_template('contract/order_show.html', order=order,posts=orderfiles)


#合同附件上传
@contractView.route('/order_upfiles/<int:oid>',methods=["GET","POST"])
@is_login
def order_upfiles(oid):
    uid = session.get('user_id')
    form=OrderupfileForm()
    order = Orders.query.filter(Orders.id == oid).first()
    form.title.data=order.title
    if form.validate_on_submit():
        try:
            f = request.files.get('upfile')
            if f:
                extension = f.filename.split('.')[-1].lower()
                if extension not in ['doc', 'xls', 'docx', 'xlsx','pdf']:
                    flash('只能上传pdf、word和excel文件!')
                oldfilename = f.filename.split('.')
                if form.title.data is not None:
                    oldfilename=form.notes.data
                newfilename = session.get('username') + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                path = os.path.join(current_app.config['UPLOADED_PATH'], datetime.datetime.now().strftime("%Y") + os.sep)

                if not os.path.exists(path):
                    os.mkdir(path)
                f.save(os.path.join(path, newfilename + '.' + extension))
                files=Files()
                files.order_id=oid
                files.notes=oldfilename
                files.path=datetime.datetime.now().strftime("%Y") + os.sep
                files.filename=newfilename+'.'+extension
                files.status='on'
                files.iuser_id=session.get('user_id')
                db.session.add(files)
                db.session.commit()
                flash('上传成功')
            else:
                flash('请选择上传附件！')
        except Exception as e:
            current_app.logger.error(e)
            flash('上传失败')
    #orderfiles = Files.query.filter(Files.order_id == oid).all()
    return render_template('contract/order_upfile.html', order=order,form=form)