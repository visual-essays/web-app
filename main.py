'''
Flask app for Visual Essays site.
Dependencies: bs4 Flask Flask-Cors html5lib requests
'''

import logging
logging.basicConfig(format='%(asctime)s : %(filename)s : \
  %(levelname)s : %(message)s', level=logging.DEBUG)
logger = logging.getLogger()

from time import time as now
from flask import Flask, request
from flask_cors import CORS
from bs4 import BeautifulSoup

import requests
logging.getLogger('requests').setLevel(logging.WARNING)

app = Flask(__name__)
CORS(app)

api_endpoint = 'https://api.visual-essays.net'
api_endpoint = 'http://localhost:8000'

# Prefix for site content
prefix = 'visual-essays/content'

def _add_link(soup, href, attrs=None):
  link = soup.new_tag('link')
  link.attrs = {**{'href':href}, **(attrs if attrs else {})}
  soup.head.append(link)

def _set_css(soup):
  # Remove default stylesheets
  # for el in soup.find_all('link', {'rel':'stylesheet'}):
  #  if 'visual-essays' in el.attrs['href']: el.decompose()
  # Add custom stylesheet
  _add_link(soup, '/static/css/custom.css', {'rel':'stylesheet'})

def _set_favicon(soup):
  # Remove default favicon
  for el in soup.find_all('link', {'rel':'icon'}): el.decompose()
  # Add custom favicon
  _add_link(soup, '/static/images/favicon.ico', {'rel':'icon'})

def _add_default_footer(soup):
  main = soup.find('main')
  main.append(soup.new_tag('ve-footer'))

def _customize_response(html):
  '''Perform any post-processing of API-generated HTML.'''
  # parse API-generated HTML with BeautifulSoup
  #   https://beautiful-soup-4.readthedocs.io/en/latest/
  soup = BeautifulSoup(html, 'html5lib')
  # perform custom updates to api-generated html
  # _set_css(soup)
  # _set_favicon(soup)
  _add_default_footer(soup)
  return str(soup)

def _get_html(path, base_url):
  api_url = f'{api_endpoint}/html{path}?prefix={prefix}&base={base_url}'
  resp = requests.get(api_url)
  return resp.text if resp.status_code == 200 else ''

@app.route('/<path:path>')
@app.route('/')
def render_html(path=None):
  start = now()
  base_url = f'/{"/".join(request.base_url.split("/")[3:])}'
  if base_url != '/' and not base_url.endswith('/'): base_url += '/'
  path = f'/{path}' if path else '/'
  html = _get_html(path, base_url)
  html = _customize_response(html)
  logger.info(f'render: api_endpoint={api_endpoint} base_url={base_url} \
  prefix={prefix} path={path} elapsed={round(now()-start, 3)}')
  return html

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=8080)
