#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Flask app for Visual Essays site.
Dependencies: bs4 expiringdict Flask Flask-Cors html5lib PyYAML requests serverless_wsgi
'''

import logging
logging.basicConfig(format='%(asctime)s : %(filename)s : \
  %(levelname)s : %(message)s', level=logging.DEBUG)
logger = logging.getLogger()

import os
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

from time import time as now
from flask import Flask, redirect, request, send_from_directory
from flask_cors import CORS
import argparse
import yaml
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from expiringdict import ExpiringDict

import requests
logging.getLogger('requests').setLevel(logging.WARNING)

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)

try:
  from serverless_wsgi import handle_request
  def handler(event, context):
    return handle_request(app, event, context)
except:
  pass

CONFIG = yaml.load(open(f'{SCRIPT_DIR}/config.yaml', 'r').read(), Loader=yaml.FullLoader)

API_ENDPOINT = 'https://api.juncture-digital.org'
PREFIX = 'visual-essays/essays' # Prefix for site content, typically Github username/repo
REF = ''                         # Github ref (branch)
LOCAL_CONTENT_ROOT = None

SEARCH_CACHE = ExpiringDict(max_len=1000, max_age_seconds=24 * 60 * 60)
TOOL_CACHE = ExpiringDict(max_len=1000, max_age_seconds=24 * 60 * 60)

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

def _make_pwa(soup):
  _add_link(soup, '/manifest.json', {'rel':'manifest'})
  
def _customize_response(html):
  '''Perform any post-processing of API-generated HTML.'''
  # parse API-generated HTML with BeautifulSoup
  #   https://beautiful-soup-4.readthedocs.io/en/latest/
  soup = BeautifulSoup(html, 'html5lib')
  # perform custom updates to api-generated html
  # _set_favicon(soup)
  # _set_style(soup)
  _make_pwa(soup)
  return str(soup)

def _get_local_content(path):
  '''For local development and testing.'''
  if path.endswith('/'): path = path[:-1]
  _paths = [f'{LOCAL_CONTENT_ROOT}{path}.md', f'{LOCAL_CONTENT_ROOT}{path}/README.md']
  for _path in _paths:
    if os.path.exists(_path):
      return open(_path, 'r').read()
  logger.warn(f'Local content not found: path={path}')

def _get_html(path, base_url, ref=REF, host=None, **kwargs):
  logger.info(f'API_ENDPOINT={API_ENDPOINT} host={host}')
  html = ''
  status_code = 404
  if LOCAL_CONTENT_ROOT:
    md = _get_local_content(path)
    if md: # Markdown found, convert to HTML using API
      api_url = f'{API_ENDPOINT}/html/?prefix={PREFIX}&base={base_url}'
      resp = requests.post(api_url, json={'markdown':md, 'prefix':PREFIX})
      status_code, html =  resp.status_code, resp.text if resp.status_code == 200 else ''
  else:
    api_url = f'{API_ENDPOINT}/html{path}?prefix={PREFIX}&base={base_url}'
    if ref: api_url += f'&ref={ref}'
    resp = requests.get(api_url)
    status_code, html =  resp.status_code, resp.text if resp.status_code == 200 else ''
  if status_code == 200 and 'api.juncture-digital.org' not in API_ENDPOINT:
    html = html.replace('https://unpkg.com/visual-essays/dist/visual-essays', f'http://{host.split(":")[0]}:3333/build')
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

@app.route('/manifest.json')
def pwa_manifest():
  return send_from_directory(os.path.join(app.root_path), 'manifest.json', mimetype='application/json')

@app.route('/<path:path>')
@app.route('/<path:path>/')
@app.route('/')
def render_html(path=None):
  logger.info('render_html')
  start = now()
  qargs = dict([(k, request.args.get(k)) for k in request.args])
  base_url = f'/{"/".join(request.base_url.split("/")[3:])}'
  if base_url != '/' and not base_url.endswith('/'): base_url += '/'
  path = f'/{path}' if path else '/'
  logger.info(f'render: path={path} base_url={base_url} qargs={qargs}')
  status, html = _get_html(path, base_url, host=request.host, **qargs)
  if status == 200:
    html = _customize_response(html)
  logger.debug(f'render: api_endpoint={API_ENDPOINT} base_url={base_url} \
  prefix={PREFIX} path={path} status={status} elapsed={round(now()-start, 3)}')
  return html, status

@app.route('/annotator/<path:path>')
@app.route('/editor/<path:path>')
@app.route('/media/<path:path>')
@app.route('/annotator/')
@app.route('/editor/')
@app.route('/media/')
@app.route('/annotator')
@app.route('/editor')
@app.route('/media')
def render_app(path=None):
  qargs = dict([(k, request.args.get(k)) for k in request.args])
  refresh = qargs.get('refresh','false').lower() in ('true', '')
  host = request.host.split(':')[0]
  tool = request.path.split('/')[1]
  logger.info(f'host={host} tool={tool} path={path} refresh={refresh}')
  if tool not in TOOL_CACHE or refresh:
    if host == 'localhost':
      return open(f'{app.root_path}/../tools/{tool}.html', 'r').read()
    else:
      resp = requests.get(f'https://raw.githubusercontent.com/visual-essays/tools/main/{tool}.html')
      if resp.status_code == 200:
        TOOL_CACHE[tool] = resp.text
      else: return '', resp.status_code
  return TOOL_CACHE[tool]

@app.route('/search')
def search():
  qargs = dict([(k, request.args.get(k)) for k in request.args])
  if 'domain' in qargs and qargs['domain'] in CONFIG['google_search']:
    args = {**CONFIG['google_search'][qargs['domain']], **dict(request.args)}
    url = f'https://www.googleapis.com/customsearch/v1?{urlencode(args)}'
    if url not in SEARCH_CACHE:
      SEARCH_CACHE[url] = requests.get(url).json()
    return SEARCH_CACHE[url]
  else:
    return [], 404

if __name__ == '__main__':
  logger.setLevel(logging.INFO)
  parser = argparse.ArgumentParser(description='Image Info')
  parser.add_argument('--port', help='Port', type=int, default=8080)
  parser.add_argument('--api', help='API Endpoint', default=API_ENDPOINT)
  parser.add_argument('--prefix', help='Content URL prefix', default=PREFIX)
  parser.add_argument('--content', help='Local content root', default=None)
  args = parser.parse_args()
  API_ENDPOINT = args.api
  PREFIX = args.prefix
  LOCAL_CONTENT_ROOT = os.path.abspath(args.content) if args.content else None
  print(f'\nAPI_ENDPOINT: {API_ENDPOINT}\nPREFIX: {PREFIX}\nLOCAL_CONTENT_ROOT: {LOCAL_CONTENT_ROOT}\n')
  app.run(debug=True, host='0.0.0.0', port=args.port)
