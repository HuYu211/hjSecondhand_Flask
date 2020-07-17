from flask import g,render_template
import datetime
def ops_render( template,context = {}):
    if 'current_user' in g:
        context['current_user'] = g.current_user
    return  render_template(template,**context)


def getCurrentDate(format ="%Y-%m-%d %H:%M;%S"):
    return datetime.datetime.now().strftime(format)
