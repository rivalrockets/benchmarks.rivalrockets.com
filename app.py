#!flask/bin/python
from flask import Flask, jsonify, abort, url_for

app = Flask(__name__)

machines = [
    {
        'id': 1,
        'system_name': 'Caged Sun',
        'system_notes': 'Sean\'s monster build',
        'owner': 'Sean Lane'
    },
    {
        'id': 2,
        'system_name': 'Polyphonic',
        'system_notes': 'Kit\'s powerful trashcan',
        'owner': 'Kit Roed'
    }
]


# 1. basic api endpoint, list all machines
@app.route('/api/v1.0/machines', methods=['GET'])
def get_machines():
        return jsonify({'machines': [make_public_machine(machine) for machine in machines]})


# 2. more intersting API endpoint, select single machine
@app.route('/api/v1.0/machines/<int:machine_id>', methods=['GET'])
def get_machine(machine_id):
    machine = [machine for machine in machines if machine['id'] == machine_id]
    if len(machine) == 0:
        abort(404)
    return jsonify({'machine': machine[0]})


# 4. a POST method for adding a new machine into our "database"
from flask import request

@app.route('/api/v1.0/machines', methods=['POST'])
def create_machine():
    if not request.json or not 'system_name' in request.json:
        abort(400)
    machine = {
        'id': machines[-1]['id'] + 1,
        'system_name': request.json['system_name'],
        'system_notes': request.json.get('system_notes', ""),
        'owner': request.json.get('owner', "")
    }
    machines.append(machine)
    return jsonify({'machine': machine}), 201


# 5. a PUT method for updating existing machine
import six

@app.route('/api/v1.0/machines/<int:machine_id>', methods=['PUT'])
def update_machine(machine_id):
    machine = [machine for machine in machines if machine['id'] == machine_id]
    if len(machine) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'system_name' in request.json and not isinstance(request.json['system_name'], six.string_types):
        abort(400)
    if 'system_notes' in request.json and not isinstance(request.json['system_notes'], six.string_types):
        abort(400)
    if 'owner' in request.json and not isinstance(request.json['owner'], six.string_types):
        abort(400)
    machine[0]['system_name'] = request.json.get('system_name', machine[0]['system_name'])
    machine[0]['system_notes'] = request.json.get('system_notes', machine[0]['system_notes'])
    machine[0]['owner'] = request.json.get('owner', machine[0]['owner'])
    return jsonify({'machine': machine[0]})


# 6. a DELETE method
@app.route('/api/v1.0/machines/<int:machine_id>', methods=['DELETE'])
def delete_machine(machine_id):
    machine = [machine for machine in machines if machine['id'] == machine_id]
    if len(machine) == 0:
        abort(404)
    machines.remove(machine[0])
    return jsonify({'result': True})


# 3. improved 404 erorr handler that responds with JSON
from flask import make_response

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


# 7. A function to generate machine json with public uri for ident
def make_public_machine(machine):
    new_machine = {}
    for field in machine:
        if field == 'id':
            new_machine['uri'] = url_for('get_machine', machine_id=machine['id'], _external=True)
        else:
            new_machine[field] = machine[field]
    return new_machine

if __name__ == '__main__':
    app.run(debug=True)
