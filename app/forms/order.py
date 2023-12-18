# -*- coding: utf-8 -*-
from wtforms import StringField,PasswordField,SubmitField,Form,widgets,SelectField,FileField,TextAreaField,DateField,IntegerField,FloatField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired,Length,NumberRange

class OrderForm(FlaskForm):
    #username = StringField( validators=[DataRequired(), Length(1, 20)])
    customername=StringField(label='客户名称:',
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control','readonly': True}
    )
    title = StringField(label='合同名称:',
        validators=[
            DataRequired(message='合同名称不能为空'),
            Length(min=2, max=200, message='合同名称长度必须大于%(min)d且小于%(max)d')
        ],
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control',
                   "placeholder":"输入合同名称"}
    )
    ordernumber = StringField(label='合同号:',
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control',
                   "placeholder":"输入合同号"}
    )
    name = StringField(label='经办人:',
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control',
                   "placeholder":"输入经办人"}
    )
    fee1 =FloatField('合同金额',validators=[NumberRange(min=0, max=10000000, message='金额只能为0-10000000')],
                         render_kw={'class': 'form-control', 'placeholder': '金额只能为0-10000000'},default=0)
    words = IntegerField(label='合同字数:', validators=[NumberRange(min=0, max=100000, message='字数只能为0-100000')],
                         render_kw={'class': 'form-control', 'placeholder': '字数只能为0-100000'},default=0)

    notes=TextAreaField(label='合同说明:',
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control',
                   "placeholder":"输入合同说明"})
    contract_date  = DateField('签订日期', format='%Y-%m-%d',validators=[DataRequired('日期不能为空')],
                            render_kw={'class': 'form-control','height':'60px'})
    submit = SubmitField('提交',render_kw={'class':'btn btn-block btn-info'})

class OrderSearchForm(FlaskForm):
    title = StringField(label='合同标题:',
        render_kw={'class': 'form-control',
                   "placeholder":"输入合同标题"}
    )
    status=SelectField(label='合同状态：',render_kw={'class': 'form-control'},
                           choices=[('己审','己审' ), ('未审','未审' ),( '待审','待审'), ('完成', '完成'),('作废', '作废')])
    submit = SubmitField('提交', render_kw={'class': 'btn btn-block btn-info'})