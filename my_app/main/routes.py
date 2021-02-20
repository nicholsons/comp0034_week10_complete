from datetime import datetime, timedelta

import requests
from flask import Blueprint, render_template
from flask_login import current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/', defaults={'name': 'Anonymous'})
@main_bp.route('/<name>')
def index(name):
    if not current_user.is_anonymous:
        name = current_user.firstname

    api_key = ''  # place your API key here
    search = 'recycling'
    newest = datetime.today().strftime('%Y-%m-%d')
    oldest = (datetime.today() - timedelta(hours=1)).strftime('%Y-%m-%d')
    sort_by = 'publishedAt'
    url = f'https://newsapi.org/v2/everything?q={search}&from={oldest}&to={newest}&sortBy={sort_by}'

    response = requests.get(url, headers={
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(api_key)
    })
    news = response.json()
    return render_template('index.html', title='Home page', name=name, news=news)
