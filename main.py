from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# storing the data store
items = []

# display all items
@app.route('/api/items', methods=['GET'])
def get_items():
    return jsonify({'items': items})

# create a new item
@app.route('/api/items', methods=['POST'])
def create_item():
    if not request.json or not 'name' in request.json:
        abort(400)
    new_item = {
        'id': len(items) + 1,
        'name': request.json['name'],
        'description': request.json.get('description', "")
    }
    items.append(new_item)
    return jsonify(new_item), 201

# for the existing item
@app.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = next((item for item in items if item['id'] == item_id), None)
    if item is None:
        abort(404)
    if not request.json:
        abort(400)
    item['name'] = request.json.get('name', item['name'])
    item['description'] = request.json.get('description', item['description'])
    return jsonify(item)

# for the existing item
@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    global items
    item = next((item for item in items if item['id'] == item_id), None)
    if item is None:
        abort(404)
    items = [item for item in items if item['id'] != item_id]
    return jsonify({'result': True})

if __name__ == '__main__':
    app.run(debug=True)
