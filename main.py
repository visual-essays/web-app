#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s : %(filename)s : %(levelname)s : %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

import os
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

import argparse

from time import time as now
from flask import Flask, request
from flask_cors import CORS

from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)
app.url_map.strict_slashes = False

api_endpoint = 'https://api.visual-essays.net'

# Github settings for site content
gh_acct = 'rdsnyder'
gh_repo = 'essays'

import requests
logging.getLogger('requests').setLevel(logging.WARNING)

def _add_link(soup, href, attrs=None):
  link = soup.new_tag('link')
  link.attrs = {**{'href':href}, **(attrs if attrs else {})}
  soup.head.append(link)

def _set_css(soup):
  # Remove default stylesheets
  # for el in soup.find_all('link', {'rel':'stylesheet'}):
  #  if el.attrs['href'].startswith('https://visual-essays.net/static/css'): el.decompose()
  # Add custom stylesheet
  _add_link(soup, '/static/css/custom.css', {'rel':'stylesheet'})

def _set_favicon(soup):
  # Remove default favicon
  for el in soup.find_all('link', {'rel':'icon'}): el.decompose()
  # Add custom favicon
  _add_link(soup, '/static/images/favicon.ico', {'rel':'icon'})

def _customize(html):
  '''Perform any post-processing of API-generated HTML.'''
  # parse API-generated HTML with BeautifulSoup https://beautiful-soup-4.readthedocs.io/en/latest/
  soup = BeautifulSoup(html, 'html5lib')
  # perform custom updates to generated html
  _set_css(soup)
  _set_favicon(soup)
  logger.debug(soup.prettify())
  return str(soup)

def _load_path(path, base_url):
  api_url = f'{api_endpoint}/html{path}?acct={gh_acct}&repo={gh_repo}&base={base_url}'
  resp = requests.get(api_url)
  logger.info(resp.status_code)
  return resp.text if resp.status_code == 200 else ''

@app.route('/<path:path>')
@app.route('/')
def render_html(path=None):
  start = now()
  base_url = f'/{"/".join(request.base_url.split("/")[3:])}'
  if base_url != '/' and not base_url.endswith('/'): base_url += '/'
  path = f'/{path}' if path else '/'
  logger.info(f'render: api_endpoint={api_endpoint} base_url={base_url} acct={gh_acct} repo={gh_repo} path={path} elapsed={round(now()-start, 3)}')
  return _customize(_load_path(path, base_url))
  
if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Markdown render service')
  parser.add_argument('--port', help='Port', type=int, default=8080)
  args = parser.parse_args()
  app.run(debug=True, host='0.0.0.0', port=args.port)
