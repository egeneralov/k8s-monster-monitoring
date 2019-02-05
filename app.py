import os
import subprocess
import json
from flask import Flask, abort, jsonify


def get_statefulsets(namespace):
  """
  namespace = 'kafka-k8s-stage-2'
  print(
    json.dumps(
      get_statefulsets(namespace),
      indent = 2
    )
  )
  """
  
  command = 'kubectl get statefulsets.apps -n {}'.format(namespace)
  result = []
  
  output = subprocess.check_output(
    command.split()
  ).decode()
  
  
  for line in output.split('\n'):
    try:
      name, desired, current, age = line.split()
    except ValueError:
      print(line)
      continue
    if name == "NAME" or name == '':
      continue
    
    if desired == current:
      alive = 1
    else:
      alive = 0
  
    result.append({
      'name': name,
      'alive': alive,
      'desired': int(desired),
      'current': int(current),
      'age': age
    })
  return result


def get_deployments(namespace):
  """
  namespace = 'core2-stage-2'
  print(
    json.dumps(
      get_deployments(namespace),
      indent = 2
    )
  )
  """
  
  command = 'kubectl get deployments.apps -n {}'.format(namespace)
  result = []
  
  output = subprocess.check_output(
    command.split()
  ).decode()
  
  
  for line in output.split('\n'):
    try:
      name, desired, current, uptodate, available, age = line.split()
    except ValueError:
      print(line)
      continue
    if name == "NAME" or name == '':
      continue
  
    if desired == current == uptodate == available:
      alive = 1
    else:
      alive = 0
  
    result.append({
      'name': name,
      'alive': alive,
      'desired': int(desired),
      'current': int(current),
      'up-to-date': int(uptodate),
      'available': int(available),
      'age': age
    })
  return result



def get_ns_names():
  command = 'kubectl get ns -o json'
  ns = []
  raw = subprocess.check_output(
    command.split()
  ).decode()
  data = json.loads(raw)
  for p_ns in data['items']:
    ns.append(
      p_ns['metadata']['name']
    )
  return ns


app = Flask(__name__)


@app.route('/')
def ok():
  return "ok"



@app.route('/namespaces/')
def get_namespaces():
  return jsonify(
    get_ns_names()
  )

@app.route('/<namespace>/')
def get_all_resources_in_namespace(namespace):
  return jsonify({
    'deployments': get_deployments(namespace),
    'statefullsets': get_statefulsets(namespace)
  })


@app.route('/<namespace>/<resource>/')
def get_resource_in_namespace(namespace, resource):
  all_resources = {
    'deployment': get_deployments,
    'deployments': get_deployments,
    'statefullset': get_statefulsets,
    'statefullsets': get_statefulsets
  }
  if resource not in all_resources.keys():
    abort(400)

  action = all_resources[resource]
  return jsonify(action(namespace))




@app.route('/<namespace>/<resource>/<name>/')
def get_resource_in_namespace_by_name(namespace, resource, name):
  all_resources = {
    'deployment': get_deployments,
    'deployments': get_deployments,
    'statefullset': get_statefulsets,
    'statefullsets': get_statefulsets
  }
  if resource not in all_resources.keys():
    abort(400)

  action = all_resources[resource]
  resource = action(namespace)
  result = {}
  for payload in action(namespace):
    result[
      payload['name']
    ] = payload
  return jsonify(result[name])


@app.route('/<namespace>/<resource>/<name>/<field>/')
def get_field_in_resource_in_namespace_by_name(namespace, resource, name, field):
  all_resources = {
    'deployment': get_deployments,
    'deployments': get_deployments,
    'statefullset': get_statefulsets,
    'statefullsets': get_statefulsets
  }
  if resource not in all_resources.keys():
    abort(400)

  action = all_resources[resource]
  resource = action(namespace)
  result = {}
  for payload in action(namespace):
    result[
      payload['name']
    ] = payload
  
  resource = result[name]
  if field not in resource.keys():
    abort(400)
  
  return jsonify(
    resource[field]
  )






@app.route('/zabbix/namespaces/')
def zabbix_lld_get_namespaces():
  result = {"data":[]}
  for ns in get_ns_names():
    result['data'].append(
      {"{#NAMESPACE}": ns}
    )
  return jsonify(result)



@app.route('/zabbix/<namespace>/<resource>/')
def zabbix_lld_get_resource_in_namespace(namespace, resource):
  all_resources = {
    'deployment': get_deployments,
    'deployments': get_deployments,
    'statefullset': get_statefulsets,
    'statefullsets': get_statefulsets
  }
  if resource not in all_resources.keys():
    abort(400)

  action = all_resources[resource]
  result = {"data":[]}
  for rs in action(namespace):
    try:
      result['data'].append({
        "{#RESOURCE}": resource,
        "{#NAMESPACE}": namespace,
        "{#NAME}": rs['name'],
        "{#ALIVE}": rs['alive'],
        "{#AGE}": rs['age'],
        "{#AVAILABLE}": rs['available'],
        "{#CURRENT}": rs['current'],
        "{#DESIRED}": rs['desired'],
        "{#UPTODATE}": rs['up-to-date']
      })
    except:
      result['data'].append({
        "{#RESOURCE}": resource,
        "{#NAMESPACE}": namespace,
        "{#NAME}": rs['name'],
        "{#ALIVE}": rs['alive'],
        "{#AGE}": rs['age'],
        "{#CURRENT}": rs['current'],
        "{#DESIRED}": rs['desired'],
      })
  return jsonify(result)




if __name__ == '__main__':
  app.run(
    port = os.environ.get('PORT', '8080'),
    host = os.environ.get('BIND', '0.0.0.0'),
    debug = True
  )

