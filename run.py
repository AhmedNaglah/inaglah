from flask import Flask, request, flash, url_for, jsonify
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_sock import Sock
from chelper.st_controller import getTopGenes, getTopCells, getTopGenesGiven, getTopCellsGiven
import json
from flask_cors import CORS

app = Flask(__name__, template_folder='./templates', static_folder='./static')
cors = CORS(app,resources={r"/*":{"origins":"*"}})
sock = Sock(app)

""" db = SQLAlchemy()
DB_NAME = "database.db"

if not path.exists('./' + DB_NAME):
    db.create_all(app=app)
    print('Created Database!') """

cid = 0
gid = 0

def parsePolygon(d):
    temp = "<svg><polygon points=\"13457,6389 13414,6393 13397,6402 13385,6407 13360,6427 13323,6465 13306,6488 13300,6500 13282,6530 13270,6544 13265,6562 13256,6574 13249,6586 13239,6613 13232,6637 13233,6762 13239,6786 13251,6819 13258,6831 13270,6846 13295,6867 13324,6880 13363,6900 13389,6907 13531,6906 13551,6900 13585,6876 13604,6862 13625,6850 13640,6838 13666,6819 13681,6807 13702,6783 13712,6773 13721,6758 13735,6732 13746,6701 13750,6678 13749,6573 13743,6543 13735,6510 13731,6494 13726,6484 13715,6469 13695,6450 13676,6442 13657,6431 13627,6422 13601,6409 13576,6403 13622.4,6299.5 13554,6393 13505,6389 13457,6389\"></polygon></svg>"
    polygon = d.replace("<svg><polygon points=\"", "").replace("\"></polygon></svg>", "").split(" ")
    print(polygon)
    polygon = [ tuple(map(float, k.split(",")))   for k in polygon]
    return polygon

@app.route("/")
def hello_world():
    return render_template('align_patch.html')

@app.route("/patho_generative_ai_liver")
def patho_generative_ai_liver():
    return render_template('patho_generative_ai_liver.html', slide1="static/assets/13.dzi", slide2="static/assets/39.dzi", slide4="static/assets/virtualtrichrome.dzi")

@app.route("/patho_generative_ai_prostate")
def patho_generative_ai_prostate():
    return render_template('patho_generative_ai_prostate.html', slide1="static/assets/he.dzi", slide2="static/assets/pin4.dzi", slide4="static/assets/virtualpin4f.dzi")

@app.route("/patho_education_virtual_biopsy")
def patho_education_virtual_biopsy():
    return render_template('patho_education_virtual_biopsy.html', slide1="static/assets/he.dzi", slide2="static/assets/pin4.dzi", slide4="static/assets/virtualpin4f.dzi")


@sock.route('/echo')
def echo(ws):
    while True:
        data = ws.receive()
        ws.send(data)

compartment_data = 'compartmentdata'
gene_data = 'genedata'

@sock.route('/get_compartment_data')
def get_compartment_data(ws):
    global compartment_data, cid
    while True:
        data = ws.receive()
        ws.send(f"{compartment_data}_{cid}")

@sock.route('/get_gene_data_given')
def get_gene_data_given(ws):
    global gene_data
    while True:
        data = ws.receive()
        polygon = parsePolygon(data)
        names, values = getTopGenesGiven(polygon, 10)
        names.extend(values.tolist())
        ws.send(names)

@sock.route('/get_gene_data')
def get_gene_data(ws):
    global gene_data
    while True:
        data = ws.receive()
        names, values = getTopGenes(int(data), 10)
        names.extend(values.tolist())
        ws.send(names)

@sock.route('/get_cell_data_given')
def get_cell_data_given(ws):
    global gene_data
    while True:
        data = ws.receive()
        polygon = parsePolygon(data)
        names, values = getTopCellsGiven(polygon, 10)
        names.extend(values.tolist())
        ws.send(names)

@sock.route('/get_cell_data')
def get_cell_data(ws):
    global gene_data
    while True:
        data = ws.receive()
        names, values = getTopCells(int(data), 10)
        names.extend(values.tolist())
        ws.send(names)


@sock.route('/update_compartment')
def update_compartment(ws):
    global cid
    while True:
        data = ws.receive()
        cid = data
        ws.send(f'success, cid updated {cid}')

@sock.route('/update_gene')
def update_gene(ws):
    global gid
    while True:
        data = ws.receive()
        gid = data
        ws.send(f'success, gid updated {gid}')

@app.route("/pathost")
def pathost_modular():
    compartment_id = request.args.get('compartment_id')
    print("render")
    print(request.args.get('compartment_id'))
    if compartment_id==None:
        print('HERE at None')
        compartment_id = 0
    gene_id = request.args.get('gene_id')
    if gene_id==None:
        gene_id = 0
        print('HERE at None')
    return render_template('pathost_modular.html', compartment_id=compartment_id, gene_id=gene_id)

@app.route('/reload', methods=['GET', 'POST'])
def reload():
    if request.method == 'POST':
        request_data = request.get_json()
        print(request_data)
        compartment_id = request_data['compartment_id']
        gene_id = request_data['gene_id']
        return app.redirect(url_for("pathost_modular", compartment_id=int(compartment_id)+10, gene_id=int(gene_id)+10))

if __name__ == '__main__':
    sock.run(debug=True, host="0.0.0.0")

