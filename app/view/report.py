from datetime import datetime

from flask import Blueprint, render_template, current_app
from jinja2 import Markup, Environment, FileSystemLoader
# from pyecharts.faker import Faker
from pyecharts.globals import CurrentConfig
from pyecharts import options as opts
from pyecharts.charts import Bar, Pie, Line
from sqlalchemy import func, create_engine
from sqlalchemy.sql.elements import and_

from app.models.bill import Fee2
from app.models.contract import Orders
from app.models.system import Groups

# 关于 CurrentConfig，可参考 [基本使用-全局变量]
CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("app/templates/pyecharts"))

report_bp = Blueprint('report', __name__)


@report_bp.route('/report/test', methods=["GET", "POST"])
def report_test():
    c = bar_base()
    return Markup(c.render_embed())


def bar_base() -> Bar:
    # x = ["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子", "hehe"]
    # y1 = [5, 20, 36, 10, 75, 90, 44]
    # y2 = [15, 25, 16, 55, 48, 8, 60]
    x = []
    y1 = []
    y2 = []
    sum11 = func.sum(Orders.Fee11).label('sum11')
    sum41 = func.sum(Orders.Fee41).label('sum41')
    fee_sum = Orders.query.with_entities(Orders.group_id, sum11, sum41).group_by(Orders.group_id).all()
    for f in fee_sum:
        gs = Groups.query.filter(Groups.id == f.group_id).first()
        x.append(gs.groupname)
        y1.append(f.sum11)
        y2.append(f.sum41)
    c = (
        Bar()
        .add_xaxis(x)
        .add_yaxis("合同金额", y1)
        .add_yaxis("到账金额", y2)
        .set_global_opts(title_opts=opts.TitleOpts(title="", subtitle=""))
    )
    return c


@report_bp.route("/report/barChart")
def get_bar_chart():
    c = bar_base()
    return c.dump_options_with_quotes()


@report_bp.route("/report/line")
def get_line():
    # x_data = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    # y_data = [820, 932, 901, 934, 1290, 1330, 1320]
    ##
    x_data = []
    y_data = []
    sum11 = func.sum(Orders.Fee11).label('sum11')
    fee_sum = Orders.query.with_entities(Orders.group_id, sum11).group_by(Orders.group_id).all()
    for f in fee_sum:
        gs = Groups.query.filter(Groups.id == f.group_id).first()
        x_data.append(gs.groupname)
        y_data.append(f.sum11)

    line = (
        Line()
        .set_global_opts(
            tooltip_opts=opts.TooltipOpts(is_show=False),
            xaxis_opts=opts.AxisOpts(type_="category"),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        )
        .add_xaxis(xaxis_data=x_data)
        .add_yaxis(
            series_name="总合同金额",
            y_axis=y_data,
            symbol="emptyCircle",
            is_symbol_show=True,
            label_opts=opts.LabelOpts(is_show=False)
        ))
    return line.dump_options_with_quotes()


@report_bp.route("/report/pie")
def get_pie():
    x_data = []
    y_data = []
    sum11 = func.sum(Orders.Fee11).label('sum11')
    fee_sum = Orders.query.with_entities(Orders.group_id, sum11).group_by(Orders.group_id).all()
    for f in fee_sum:
        gs = Groups.query.filter(Groups.id == f.group_id).first()
        x_data.append(gs.groupname)
        y_data.append(f.sum11)
    c = (
        Pie()
        .add("总合同金额", [list(z) for z in zip(
            x_data,
            y_data
        )])
        .set_global_opts(title_opts=opts.TitleOpts(title=""))
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )
    return c.dump_options_with_quotes()


@report_bp.route("/report/list")
def report_perf():
    t_format = '%Y-%m-%d'
    date_b = '2023-12-01'
    date_e = '2023-12-11'
    engine = create_engine(current_app.config['SQLALCHEMY_DATABASE_URI'], echo=False)
    with engine.connect() as conn:
        result_proxy = conn.execute("select a.*,fee4.fee,fee4.feedate,fee3.id from "
                                    "(select order_id,"
                                    "group_concat(concat_ws(',',feedate) order by feedate asc) as 'dates',"
                                    "type,sum(fee) as 'fees',0 as 'bid',round(sum(fee)/1.06,2) as 'fee106',"
                                    "0.16 as 'ratio',round(sum(fee)/1.06,2)*0.16 as 'perf' "
                                    "from fee2 group by order_id,type order by order_id,type) "
                                    "a,fee4,fee3 "
                                    "where  a.order_id=fee4.order_id and fee4.order_id=fee3.order_id")
        result = result_proxy.fetchall()
        # for item in result:
        #    print(item)
    return render_template('report/list.html', result=result)
