# -*- coding: utf-8 -*-
from wtforms import StringField,PasswordField,SubmitField,Form,widgets,SelectField,FileField,TextAreaField,DateField,IntegerField,FloatField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired,Length,NumberRange


class WordsForm(FlaskForm):

    words = IntegerField(label='字数发生额:', validators=[NumberRange(min=0, max=100000, message='字数只能为0-100000')],
                         render_kw={'class': 'form-control', 'placeholder': '字数只能为0-100000'},default=0)

    notes=TextAreaField(label='备注:',
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control',
                   "placeholder":"备注"})
    fee_date  = DateField('发生日期', format='%Y-%m-%d',validators=[DataRequired('日期不能为空')],
                            render_kw={'class': 'form-control','height':'60px'})
    submit = SubmitField('提交',render_kw={'class':'btn btn-block btn-info'})

class FeeForm(FlaskForm):

    fee =FloatField('发生金额',validators=[NumberRange(min=-9999999, max=9999999, message='金额只能为-9999999至9999999')],
                         render_kw={'class': 'form-control', 'placeholder': '金额只能为-9999999至9999999'},default=0)
    notes=TextAreaField(label='备注:',
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control',
                   "placeholder":"备注"})
    fee_date  = DateField('发生日期', format='%Y-%m-%d',validators=[DataRequired('日期不能为空')],
                            render_kw={'class': 'form-control','height':'60px'})
    submit = SubmitField('提交',render_kw={'class':'btn btn-block btn-info'})