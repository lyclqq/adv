# -*- coding: utf-8 -*-
from wtforms import StringField,PasswordField,SubmitField,Form,widgets,SelectField,FileField,TextAreaField,DateField,IntegerField,FloatField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired,Length,NumberRange


class WordsForm(FlaskForm):
    title = StringField(label='合同名称:',
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control',
                   "placeholder":"输入合同名称",'readonly':True}
    )
    ordernumber = StringField(label='合同号:',
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control','readonly':True}
    )
    wordnumber = IntegerField(label='合同字数:', render_kw={'class': 'form-control', 'readonly':True})
    wordcount = IntegerField(label='己发字数:', render_kw={'class': 'form-control', 'readonly': True})
    words = IntegerField(label='字数发生额:', validators=[NumberRange(min=0, max=100000, message='字数只能为0-100000')],
                         render_kw={'class': 'form-control', 'placeholder': '字数只能为0-100000'},default=0)

    notes=TextAreaField(label='备注:',
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control',
                   "placeholder":"备注"})
    fee_date  = DateField('发生日期', format='%Y-%m-%d',validators=[DataRequired('日期不能为空')],
                            render_kw={'class': 'form-control','height':'60px'})
    type=SelectField(label='类型：',render_kw={'class': 'form-control'},
                           choices=[('order','合同字数' ), ('publish','己发字数' )])
    submit = SubmitField('提交',render_kw={'class':'btn btn-block btn-info'})