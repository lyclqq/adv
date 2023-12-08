# -*- coding: utf-8 -*-
from wtforms import StringField,PasswordField,SubmitField,Form,widgets,SelectField,FileField,TextAreaField,DateField,IntegerField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired,Length

#登陆
class CustomerForm(FlaskForm):
    #username = StringField( validators=[DataRequired(), Length(1, 20)])
    name = StringField(label='客户名称:',
        validators=[
            DataRequired(message='客户名称不能为空'),
            Length(min=2, max=40, message='客户名称长度必须大于%(min)d且小于%(max)d')
        ],
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control',
                   "placeholder":"输入客户名称"}
    )
    notes=TextAreaField(label='客户说明:',
        validators=[
            Length(max=250, message='客户说明长度必须大于%(min)d')
        ],
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control',
                   "placeholder":"输入客户说明"})
    submit = SubmitField('提交',render_kw={'class':'btn btn-block btn-info'})

class OrderSearchForm(FlaskForm):
    title = StringField(label='合同标题:',
        render_kw={'class': 'form-control',
                   "placeholder":"输入合同标题"}
    )
    status=SelectField(label='合同状态：',render_kw={'class': 'form-control'},
                           choices=[('己审','己审' ), ('未审','未审' ),( '待审','待审'), ('完成', '完成'),('作废', '作废')])
    submit = SubmitField('提交', render_kw={'class': 'btn btn-block btn-info'})
