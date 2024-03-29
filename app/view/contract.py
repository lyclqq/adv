# -*- coding: utf-8 -*-

from flask import Blueprint,render_template,current_app,url_for,redirect,session,request,flash,g
import json
import os
from functools import wraps
from app.common import is_login,ins_logs,month_difference
from app import db
from app.models.bill import Fee1
from app.models.contract import Customers,Orders
from app.models.other import Files
from app.models.system import Systeminfo
from app.forms.customer import CustomerForm,CustomersearchForm
from app.forms.fee import Fee1Form,FeeSearchForm
from app.forms.order import OrderForm,OrderSearchForm,OrderupfileForm
from app.view import search_orders
import datetime

contractView=Blueprint('contract_admin',__name__)

#客户管理
@contractView.route('/customer_admin',endpoint='customer_admin',methods=["GET","POST"])
@is_login
def customer_admin():
    uid = session.get('user_id')
    customers=Customers()
    page = request.args.get('page', 1, type=int)
    form=CustomersearchForm()
    title=None
    if form.validate_on_submit():
        page=1
        title=form.name.data
    pagination=customers.search_customers( keywords=title,page=page,all=False)
    result = pagination.items
    return render_template('contract/customer_admin.html', page=page, pagination=pagination, posts=result,form=form)

#合同管理
@contractView.route('/order_admin',methods=["GET","POST"])
@is_login
def order_admin():
    #print('menu is '+str(session.get('menu')))
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    form=OrderSearchForm()
    pagination,page=search_orders(searchform=form,page=page)
    return render_template('contract/order_admin.html', page=page, pagination=pagination, form=form)


#客户状态
@contractView.route('/customer_status/<int:cuid>')
@is_login
def customer_status(cuid):
    uid=session.get('user_id')
    try:
        customer = Customers.query.filter_by(id=cuid).first_or_404()
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
    customer = Customers.query.filter(Customers.id == cuid).first_or_404()
    form=CustomerForm()
    if form.validate_on_submit():
        try:

            customer.name=form.name.data
            customer.notes=form.notes.data

            db.session.commit()
            flash('修改成功.', 'success')
            ins_logs(uid,'修改客户'+str(cuid),type='contract')
        except Exception as e:
            current_app.logger.error(e)
            flash('修改失败')
    form.name.data=customer.name
    form.notes.data=customer.notes
    if customer.status=='stay':
        form.submit.render_kw = {'class': 'form-control', 'disabled': False}
    else:
        form.submit.render_kw = {'class': 'form-control', 'disabled': True}
        flash('状态不对，不能修改!')
    return render_template('contract/customer_edit.html',form=form)

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
        try:
            systeminfo = Systeminfo.query.filter(Systeminfo.id == 1).first()
            if month_difference(systeminfo.systemmonth, form.contract_date.data) >= 1:
                flash('不能晚于系统当月！.', 'success')
            else:
                order = Orders()
                order.name = form.name.data
                order.title = form.title.data
                order.notes = form.notes.data
                order.Fee11 = form.fee1.data
                order.cutomer_id = cuid
                order.iuser_id = uid
                order.contract_date = form.contract_date.data
                order.wordnumber = form.words.data
                order.ordernumber=form.ordernumber.data
                order.status = '未审'
                order.group_id = groupid
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
            systeminfo = Systeminfo.query.filter(Systeminfo.id == 1).first()
            if month_difference(systeminfo.systemmonth, form.contract_date.data) >= 1:
                flash('不能晚于系统当月！.', 'success')
            else:
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
                order.wordnumber=form.words.data
                order.ordernumber=form.ordernumber.data
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
def order_edit(oid):
    uid = session.get('user_id')
    order=Orders.query.filter(Orders.id==oid).first_or_404()
    form=OrderForm()
    form.customername.data = '1111'  # 只是为了验证加上
    if form.validate_on_submit():
        try:
            if order.status=="未审":
                order.notes=form.notes.data
                order.title=form.title.data
                order.ordernumber=form.ordernumber.data
                order.contract_date=form.contract_date.data
                order.name=form.name.data
                order.update_datetime=datetime.datetime.now()
                order.Fee11=form.fee1.data
                order.wordnumber=form.words.data
                db.session.add(order)
                db.session.commit()
                ins_logs(uid, '修改合同，orderid='+str(oid), type='contract')
                flash("修改成功")
            else:
                flash("不是未审状态，不能修改")
        except Exception as e:
            current_app.logger.error(e)
            flash('修改失败')
    else:
        form.notes.data=order.notes
        form.title.data=order.title
        form.ordernumber.data=order.ordernumber
        form.contract_date.data=order.contract_date
        form.name.data=order.name
        form.fee1.data=order.Fee11
        form.words.data=order.wordnumber
        if order.status == "未审" and order.iuser_id==uid:
            form.submit.render_kw = {'class': 'form-control', 'disabled': False}
        else:
            form.submit.render_kw = {'class': 'form-control', 'disabled': True}
    return render_template('contract/order_edit.html',form=form)

#合同加备注
@contractView.route('/order_notes/<int:oid>',methods=["GET","POST"])
@is_login
def order_notes(oid):
    uid = session.get('user_id')
    order=Orders.query.filter(Orders.id==oid).first_or_404()
    form=OrderForm()
    form.customername.data = '1111'  # 只是为了验证加上
    if form.validate_on_submit():
        try:
            order.notes=form.notes.data
            db.session.commit()
            ins_logs(uid, '修改合同备注，orderid='+str(oid), type='contract')
            flash("修改成功")
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            flash('修改失败')
    else:
        form.notes.data=order.notes
        form.title.data=order.title
        form.title.render_kw={'class': 'form-control', 'readonly': True}
        form.ordernumber.data=order.ordernumber
        form.ordernumber.render_kw={'class': 'form-control', 'readonly': True}
        form.contract_date.data=order.contract_date
        form.contract_date.render_kw={'class': 'form-control', 'readonly': True}
        form.name.data=order.name
        form.name.render_kw = {'class': 'form-control', 'readonly': True}
        form.fee1.data=order.Fee11
        form.fee1.render_kw = {'class': 'form-control', 'readonly': True}
        form.words.data=order.wordnumber
        form.words.render_kw = {'class': 'form-control', 'readonly': True}
    return render_template('contract/order_edit.html',form=form)

#合同查看
@contractView.route('/order_show/<int:oid>',methods=["GET","POST"])
@is_login
def order_show(oid):
    uid = session.get('user_id')
    order=Orders.query.filter(Orders.id==oid).first_or_404()
    option = []

    uid = session.get('user_id')
    order=Orders.query.filter(Orders.id==oid).first_or_404()
    billfee={'value': order.Fee11,'title': order.Fee11,'itemStyle': {'color': '#a90000'}}
    option.append(billfee)
    option.append(order.Fee21)
    option.append(order.Fee31)
    option.append(order.Fee41)
    option.append(order.Fee51)
    orderfiles=Files.query.filter(Files.order_id==oid,Files.status!='off').all()
    return render_template('contract/order_show.html', order=order,posts=orderfiles,option=option)


#合同提交
@contractView.route('/order_submit/<int:oid>',methods=["GET","POST"])
@is_login
def order_submit(oid):
    uid = session.get('user_id')
    order=Orders.query.filter(Orders.id==oid).first_or_404()
    if order.status=='未审':
        try:
            order.update_datetime=datetime.datetime.now()
            order.status='待审'
            db.session.add(order)
            db.session.commit()
            ins_logs(uid, '提交成功，orderid=' + str(oid), type='contract')
        except Exception as e:
            current_app.logger.error(e)
            flash('提交失败')
    return redirect(url_for('contract_admin.order_admin'))


#合同附件上传
@contractView.route('/order_upfiles/<int:oid>',methods=["GET","POST"])
@is_login
def order_upfiles(oid):
    uid = session.get('user_id')
    form=OrderupfileForm()
    order = Orders.query.filter(Orders.id == oid).first_or_404()
    form.title.data=order.title
    if form.validate_on_submit():
        try:
            f = request.files.get('upfile')
            if f:
                extension = f.filename.split('.')[-1].lower()
                if extension not in ['doc', 'xls', 'docx', 'xlsx','pdf']:
                    flash('只能上传pdf、word和excel文件!')
                else:
                    oldfilename = f.filename
                    if form.notes.data.strip()!='':
                        oldfilename=form.notes.data.strip()
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
                    files.status='stay'
                    files.iuser_id=session.get('user_id')
                    db.session.add(files)
                    db.session.commit()
                    ins_logs(uid, '合同上传附件，orderid=' + str(oid), type='contract')
                    flash('上传成功')
            else:
                flash('请选择上传附件！')
        except Exception as e:
            current_app.logger.error(e)
            flash('上传失败')
    orderfiles = Files.query.filter(Files.order_id == oid,Files.status!='off').all()
    return render_template('contract/order_upfile.html', order=order,form=form,posts=orderfiles)


# 合同金额输入
@contractView.route('/fee1_input/<int:oid>', methods=["GET", "POST"])
@is_login
def fee1_input(oid):
    uid = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    form = Fee1Form()
    order = Orders.query.filter(Orders.id == oid).first_or_404()
    if order.status != '己审' and order.status!='完成':
        form.submit.render_kw={'class':'form-control','disabled':'true'}
    else:
        form.submit.render_kw = {'class': 'form-control'}
    if form.validate_on_submit():
        try:
            systeminfo=Systeminfo.query.filter(Systeminfo.id==1).first()
            if month_difference(systeminfo.systemmonth,form.fee_date.data)>=1:
                flash('不能晚于系统当月！.', 'success')
            else:
                fee1 = Fee1()
                fee1.order_id = oid
                fee1.status = 'stay'
                fee1.iuser_id = uid
                fee1.feedate = form.fee_date.data
                fee1.fee = form.fee.data
                fee1.notes = form.notes.data
                db.session.add(fee1)
                db.session.commit()
                flash('录入成功.', 'success')
                ins_logs(uid, '合同金额录入,id=' + str(oid), type='contract')
        except Exception as e:
            current_app.logger.error(e)
            flash('录入失败')
    pagination = Fee1.query.filter(Fee1.order_id == oid).order_by(Fee1.id.desc()).paginate(page, per_page=8)
    return render_template('contract/fee1_input.html', form=form, order=order, pagination=pagination,page=page)

# 合同金额查看
@contractView.route('/fee1_show/<int:oid>', methods=["GET", "POST"])
@is_login
def fee1_show(oid):
    uid = session.get('user_id')
    form=FeeSearchForm()
    pagerows = current_app.config['PAGEROWS']

    order = Orders.query.filter(Orders.id == oid).first_or_404()
    if form.validate_on_submit():
        page=1
        session['fee1_status']=form.status.data
        fee_status=form.status.data
    else:
        page = request.args.get('page', 1, type=int)
        if session.get('fee1_status') is None:
            fee_status='all'
        else:
            fee_status = session.get('fee1_status')
            form.status.data = fee_status
    if fee_status=='all':
        pagination = Fee1.query.filter(Fee1.order_id == oid).order_by(Fee1.id.desc()).paginate(page, per_page=pagerows)
    else:
        pagination = Fee1.query.filter(Fee1.order_id == oid,Fee1.status==fee_status).order_by(Fee1.id.desc()).paginate(page,
                                                                                                   per_page=pagerows)
    return render_template('contract/fee1_show.html', order=order, pagination=pagination,page=page,form=form)