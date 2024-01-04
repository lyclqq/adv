from flask import Blueprint
from jinja2 import Markup, Environment, FileSystemLoader
from pyecharts.faker import Faker
from pyecharts.globals import CurrentConfig
from pyecharts import options as opts
from pyecharts.charts import Bar, Pie
from sqlalchemy import func

from app.models.contract import Orders

# 关于 CurrentConfig，可参考 [基本使用-全局变量]
CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("app/templates/pyecharts"))

report_bp = Blueprint('report', __name__)


@report_bp.route('/report/test', methods=["GET", "POST"])
def report_test():
    c = bar_base()
    return Markup(c.render_embed())


def bar_base() -> Bar:
    sum11 = func.sum(Orders.Fee11).label('fee11')
    sum41 = func.sum(Orders.Fee41).label('fee41')
    fee_sum = Orders.query.with_entities(Orders.group_id, sum11, sum41).group_by(Orders.group_id).all()
    #for f in fee_sum:
    #    print(f.group_id, f.sum11, f.sum41)
    x = ["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子", "hehe"]
    y1 = [5, 20, 36, 10, 75, 90, 44]
    y2 = [15, 25, 16, 55, 48, 8, 60]
    c = (
        Bar()
        .add_xaxis(x)
        .add_yaxis("商家A", y1)
        .add_yaxis("商家B", y2)
        .set_global_opts(title_opts=opts.TitleOpts(title="Bar-基本示例", subtitle=""))
    )
    return c


@report_bp.route("/report/barChart")
def get_bar_chart():
    c = bar_base()
    return c.dump_options_with_quotes()


@report_bp.route("/report/line")
def get_line():
    from pyecharts.charts import Line
    x_data = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    y_data = [820, 932, 901, 934, 1290, 1330, 1320]
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
            series_name="dd",
            y_axis=y_data,
            symbol="emptyCircle",
            is_symbol_show=True,
            label_opts=opts.LabelOpts(is_show=False)
        ))
    return line.dump_options_with_quotes()


@report_bp.route("/report/pie")
def get_pie():
    c = (
        Pie()
        .add("", [list(z) for z in zip(Faker.choose(), Faker.values())])
        .set_global_opts(title_opts=opts.TitleOpts(title=""))
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )
    return c.dump_options_with_quotes()
