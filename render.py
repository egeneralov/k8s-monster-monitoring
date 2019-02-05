#!/usr/bin/env python

from jinja2 import Template
from requests import get
from json import dumps


def get_keys(base_url = 'https://stage-2.detokex.com/monitoring/api'):
  result = []
  for namespace in get('{}/namespaces/'.format(base_url)).json():
    for resource in ['statefullset', 'deployment']:
      key = 'k8s.discovery.{}.{}'.format(namespace, resource)
      result.append(key)
  return result


def main():
  file = '/Users/user/Downloads/zbx_export_templates.xml'
  
  with open(file) as f:
    template = Template(f.read())
  
  print(
    template.render(
      keys = get_keys()
    )
  )

if __name__ == '__main__':
  main()


