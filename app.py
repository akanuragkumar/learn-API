from flask import Flask
from concept import concept
from subject import subject
from unit import unit
from chapter import chapter



app = Flask(__name__)



@app.route('/<entity>/<entity_code>', methods=['GET'])
def main(entity, entity_code):
    if entity == 'chapters':
        return chapter(entity_code)
    if entity == 'units':
        return unit(entity_code)
    if entity == 'concepts':
        return concept(entity_code)
    if entity == 'subjects':
        return subject(entity_code)



@app.route('/healthcheck')
def healthcheck():
    return "Hello!"


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)