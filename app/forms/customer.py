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
            Length(max=250, message='客户说明长度不能大于%(max)d')
        ],
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control',
                   "placeholder":"输入客户说明"})
    submit = SubmitField('提交',render_kw={'class':'form-control'})


