import re
import pprint
import librouteros
from librouteros import connect as connect
from flask import Flask, request
from flask import render_template


# Function
def validate_formulary(data):
    pattern_ip = '^(\d{1,3}\.){3}\d{1,3}$'
    pattern_user = '^[a-zA-Z]+\.[a-zA-Z]+$'
    if re.match(pattern_ip, data['ip']):
        pass
    elif re.match(pattern_user, data['username']):
        pass
    else:
        data['error'] = 'True'
    return data


def connect(data):
    conn = librouteros.connect(
	host=data['ip'],
	username=data['username'],
	password=data['password']
    )
   
    interface = conn(cmd='/interface/ethernet/print')
    interface = [{'name':el['name'],'speed':el['speed'],'mtu':el['mtu']} for el in interface]

    ospf = conn(cmd='/routing/ospf/neighbor/print')
    ospf = [{'address':el['address'],'state':el['state'],'adjacency':el['adjacency'], 'interface':el['interface']} for el in ospf]

    ospf_lsa = conn(cmd='/routing/ospf/lsa/print')
    ospf_lsa = [{'area':el['area'],'id':el['id'],'type':el['type'], 'originator':el['originator']} for el in ospf_lsa]

    hostname = conn(cmd='/system/identity/print')
    hostname  = [{'name':el['name']} for el in hostname]

    ipaddress = conn(cmd='/ip/address/print')
    ipaddress = [{'interface':el['interface'],'network':el['network']} for el in ipaddress]

    routerboard = conn(cmd='/system/routerboard/print')
    routerboard = [{'model':el['model'],'factory-firmware':el['factory-firmware'],'current-firmware':el['current-firmware'],'upgrade-firmware':el['upgrade-firmware']} for el in routerboard]

    neighbor = conn(cmd='/ip/neighbor/print')
    neighbor = [{'identity':el['identity'],'interface':el['interface'],'platform':el['platform'],'version':el['version']} for el in neighbor]
    
    object = {}
    object['username'] = data['username']
    object['hostname'] = hostname
    object['interfaces'] = interface
    object['ipaddress'] = ipaddress
    object['neighbor'] = neighbor
    object['routerboard'] = routerboard
    object['ospf'] = ospf
    object['ospf_lsa'] = ospf_lsa
     
    for a in neighbor:
        pprint.pprint(a)
    return object

# Routes
app = Flask(__name__)
@app.route("/")
def root():
    return render_template("index.html")

@app.route("/", methods=['POST'])
def generate():
    if request.method == 'POST':
        data = {}
        data['ip'] = request.form['ip']
        data['username'] = request.form['username']
        data['password'] = request.form['password']
        data = validate_formulary(data)
        command = connect(data)
        pprint.pprint(command)
        return render_template("generate.html",data=command)

if __name__ == "__main__":
    app.run(debug=True)