from flask import Flask, jsonify, request, abort
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# In-memory data store
items = []

# Route to display all items
@app.route('/api/items', methods=['GET'])
def get_items():
    return jsonify({'items': items})

# Route to create a new item
@app.route('/api/items', methods=['POST'])
def create_item():
    if not request.json or not all(k in request.json for k in ('name', 'mobile', 'address', 'description', 'email')):
        abort(400, description="Request must be JSON and contain 'name', 'mobile', 'address', 'description', and 'email'")
    
    new_item = {
        'id': len(items) + 1,
        'name': request.json['name'],
        'mobile': request.json['mobile'],
        'address': request.json['address'],
        'description': request.json['description'],
        'email': request.json['email']
    }
    items.append(new_item)
    return jsonify(new_item), 201

# Route to update an existing item
@app.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = next((item for item in items if item['id'] == item_id), None)
    if item is None:
        abort(404, description="Item not found")
    if not request.json:
        abort(400, description="Request must be JSON")
    item['name'] = request.json.get('name', item['name'])
    item['mobile'] = request.json.get('mobile', item['mobile'])
    item['address'] = request.json.get('address', item['address'])
    item['description'] = request.json.get('description', item['description'])
    item['email'] = request.json.get('email', item['email'])
    return jsonify(item)

# Route to delete an existing item
@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    global items
    item = next((item for item in items if item['id'] == item_id), None)
    if item is None:
        abort(404, description="Item not found")
    items = [item for item in items if item['id'] != item_id]
    return jsonify({'result': True})

if __name__ == '__main__':
    app.run(port=5001, debug=True)
