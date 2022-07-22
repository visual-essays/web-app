'''
Flask app for Visual Essays site.
Dependencies: bs4 Flask Flask-Cors html5lib requests
'''

import logging
logging.basicConfig(format='%(asctime)s : %(filename)s : \
  %(levelname)s : %(message)s', level=logging.DEBUG)
logger = logging.getLogger()

import os
from time import time as now
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from serverless_wsgi import handle_request

from bs4 import BeautifulSoup

import requests
logging.getLogger('requests').setLevel(logging.WARNING)

app = Flask(__name__)
CORS(app)

def handler(event, context):
  return handle_request(app, event, context)

def api_endpoint():
  if request.host.startswith('localhost') or request.host.startswith('192.168'):
    _api_endpoint = 'http://localhost:8000'
  else:
    _api_endpoint = 'https://api.visual-essays.net' if 'visual-essays.net' in request.host else 'https://api.juncture-digital.org'
  logger.info(f'api_endpoint: host={request.host} api_endpoint={_api_endpoint}')
  return _api_endpoint

# Prefix for site content
# prefix = 'visual-essays/content'
prefix = 'a3b51252'

def _add_link(soup, href, attrs=None):
  link = soup.new_tag('link')
  link.attrs = {**{'href':href}, **(attrs if attrs else {})}
  soup.head.append(link)

def _add_script(soup, src, attrs=None):
  script = soup.new_tag('script')
  script.attrs = {**{'src':src}, **(attrs if attrs else {})}
  soup.body.append(script)

def _set_favicon(soup):
  # Remove default favicon
  for el in soup.find_all('link', {'rel':'icon'}): el.decompose()
  # Add custom favicon
  # _add_link(soup, '/static/images/favicon.svg', {'rel': 'icon', 'type':'image/svg+xml'})
  # _add_link(soup, '/static/images/favicon.ico', {'rel':'icon', 'type':'image/png'})

def _set_style(soup):
  # Remove default favicon
  for el in soup.find_all('link', {'rel':'stylesheet'}): el.decompose()
  # Add custom stylesheet
  # _add_link(soup, '/static/css/custom.css', {'rel': 'stylesheet'})

def _customize_response(html):
  '''Perform any post-processing of API-generated HTML.'''
  # parse API-generated HTML with BeautifulSoup
  #   https://beautiful-soup-4.readthedocs.io/en/latest/
  soup = BeautifulSoup(html, 'html5lib')
  # perform custom updates to api-generated html
  # _set_favicon(soup)
  # _set_style(soup)
  return str(soup)

def _get_html(path, base_url, ref=None, **kwargs):
  _api_endpoint = api_endpoint()
  api_url = f'{_api_endpoint}/html{path}?prefix={prefix}&base={base_url}'
  if ref: api_url += f'&ref={ref}'
  resp = requests.get(api_url)
  status_code, html =  resp.status_code, resp.text if resp.status_code == 200 else ''
  if status_code == 200 and _api_endpoint == 'http://localhost:8000':
    html = html.replace('https://unpkg.com/visual-essays/dist/visual-essays','http://localhost:3333/build')
  return status_code, html

@app.route('/favicon.ico')
def favicon():
  return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/robots.txt')
def robots_txt():
  return send_from_directory(os.path.join(app.root_path, 'static'), 'robots.txt', mimetype='text/plain')

@app.route('/sitemap.txt')
def sitemap_txt():
  return send_from_directory(os.path.join(app.root_path, 'static'), 'sitemap.txt', mimetype='text/plain')

@app.route('/<path:path>')
@app.route('/<path:path>/')
@app.route('/')
def render_html(path=None):
  start = now()
  qargs = dict([(k, request.args.get(k)) for k in request.args])
  base_url = f'/{"/".join(request.base_url.split("/")[3:])}'
  if base_url != '/' and not base_url.endswith('/'): base_url += '/'
  path = f'/{path}' if path else '/'
  status, html = _get_html(path, base_url, **qargs)
  if status == 200:
    html = _customize_response(html)
  logger.debug(f'render: api_endpoint={api_endpoint()} base_url={base_url} \
  prefix={prefix} path={path} status={status} elapsed={round(now()-start, 3)}')
  return html, status

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=8080)
