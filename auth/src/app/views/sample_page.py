from flask import Blueprint, render_template
from flask.views import MethodView

sample_page_blueprint = Blueprint('sample_page', __name__, url_prefix='/auth/')


class SamplePageView(MethodView):
    def get(self):
        return render_template("sample_page.html")


sample_page_blueprint.add_url_rule(
    '/sample_page/',
    endpoint='sample_page',
    view_func=SamplePageView.as_view('sample_page'),
    methods=["GET"]
)