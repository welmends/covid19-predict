from seir_prediction import predict
import json
import flask
from flask import request, jsonify
from flask import Flask


def get_predict_json(soln):
    json_list = []
    for n in soln:
        json_dict = json.dumps(
            {'S': n[0], 'E': n[1], 'I1': n[2], 'I2': n[3], 'I3': n[4], 'R': n[5], 'D': n[6]})
        json_list.append(json.loads(json_dict))
    return json_list


## Flask Config ###
app = flask.Flask(__name__)
app.config["DEBUG"] = False

### Routes ###
# http://lapisco.fortaleza.ifce.edu.br:3012/api/covid19predict
@app.route('/api/covid19predict', methods=['GET'], endpoint='apicovid19predict_routes')
def apicovid19predict_routes():
    return open('routes.html').read()

# http://lapisco.fortaleza.ifce.edu.br:3012/api/covid19predict/parameters
@app.route('/api/covid19predict/parameters', methods=['GET'], endpoint='apicovid19predict_parameters')
def apicovid19predict_parameters():
    return open('parameters.html').read()

# http://lapisco.fortaleza.ifce.edu.br:3012/api/covid19predict?IP=5&DMI=10&FM=0.8&FS=0.15&FC=0.05&TMC=0.02&T_UTI_D=7&DH=11&B1=0.33&B2=0.01&B3=0.01&PII=1&POP=8843000&TMAX=365
@app.route('/api/covid19predict/progression', methods=['GET'], endpoint='apicovid19predict_progression')
def apicovid19predict_progression():
    # params
    IP = request.args.get('IP')
    DMI = request.args.get('DMI')
    FM = request.args.get('FM')
    FS = request.args.get('FS')
    FC = request.args.get('FC')
    TMC = request.args.get('TMC')
    T_UTI_D = request.args.get('T_UTI_D')
    DH = request.args.get('DH')
    B1 = request.args.get('B1')
    B2 = request.args.get('B2')
    B3 = request.args.get('B3')
    PII = request.args.get('PII')
    POP = request.args.get('POP')
    TMAX = request.args.get('TMAX')

    # return if has no arguments
    if(IP == None or DMI == None or FM == None or FS == None or FC == None or TMC == None or T_UTI_D == None or DH == None or B1 == None or B2 == None or B3 == None or PII == None or POP == None or TMAX == None):
        return 'Missing arguments..'

    # predict
    #slon = predict(5, 10, 0.8, 0.15, 0.05, 0.02, 7, 11, 0.33, 0.01, 0.01, 1, 8843000, 365)
    slon = predict(IP, DMI, FM, FS, FC, TMC, T_UTI_D,
                   DH, B1, B2, B3, PII, POP, TMAX)

    # json
    json_list = get_predict_json(slon)

    # return
    return jsonify(json_list)


### Main ###
if __name__ == "__main__":
    app.run()
    #app.run(host='10.110.21.13', port=3012)
