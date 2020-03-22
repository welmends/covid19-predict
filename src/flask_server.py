from seir_prediction import predict_progression, predict_progression_slow
import json
import flask
from flask import request, jsonify
from flask import Flask

### Encapsulate on JSON ###


def get_predict_json_progression(soln):
    day = 0
    json_list = []
    for n in soln:
        json_dict = json.dumps(
            {'_day': 1+(day/10), 'S': n[0], 'E': n[1], 'I1': n[2], 'I2': n[3], 'I3': n[4], 'R': n[5], 'D': n[6]})
        json_list.append(json.loads(json_dict))
        day = day + 1
    return json_list


def get_predict_json_progression_slow(soln, slonSlow):
    day = 1
    json_list = []
    for n, m in zip(soln, slonSlow):
        json_dict = json.dumps(
            {'_day': 1+(day/10), 'S': n[0], 'E': n[1], 'I1': n[2], 'I2': n[3], 'I3': n[4], 'R': n[5], 'D': n[6], 'S_': m[0], 'E_': m[1], 'I1_': m[2], 'I2_': m[3], 'I3_': m[4], 'R_': m[5], 'D_': m[6]})
        json_list.append(json.loads(json_dict))
        day = day + 1
    return json_list


### Flask Config ###
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

# http://lapisco.fortaleza.ifce.edu.br:3012/api/covid19predict/progression?POP=8843000&PII=1&TMAX=365&IP=5&DMI=10&FM=0.8&FS=0.15&FC=0.05&TMC=0.02&T_UTI_D=7&DH=11&B1=0.33&B2=0.01&B3=0.01
@app.route('/api/covid19predict/progression', methods=['GET'], endpoint='apicovid19predict_progression')
def apicovid19predict_progression():
    # params
    POP = request.args.get('POP')
    PII = request.args.get('PII')
    TMAX = request.args.get('TMAX')
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

    # return if has no arguments
    if(POP == None or PII == None or TMAX == None or IP == None or DMI == None or FM == None or FS == None or FC == None or TMC == None or T_UTI_D == None or DH == None or B1 == None or B2 == None or B3 == None):
        return 'Missing arguments: {POP, PII, TMAX, IP, DMI, FM, FS, FC, TMC, T_UTI_D, DH, B1, B2, B3}'

    # predict
    #slon = predict_progression(8843000, 1, 365, 5, 10, 0.8, 0.15, 0.05, 0.02, 7, 11, 0.33, 0.01, 0.01)
    slon = predict_progression(
        POP, PII, TMAX, IP, DMI, FM, FS, FC, TMC, T_UTI_D, DH, B1, B2, B3)

    # json
    json_list = get_predict_json_progression(slon)

    # return
    return jsonify(json_list)

# http://lapisco.fortaleza.ifce.edu.br:3012/api/covid19predict/progressionSlow?POP=8843000&PII=1&TMAX=365&IP=5&DMI=10&FM=0.8&FS=0.15&FC=0.05&TMC=0.02&T_UTI_D=7&DH=11&B1=0.33&B2=0.01&B3=0.01&R1=0.3&R2=0.0&R3=0.0
@app.route('/api/covid19predict/progressionSlow', methods=['GET'], endpoint='apicovid19predict_progressionSlow')
def apicovid19predict_progressionSlow():
    # params
    POP = request.args.get('POP')
    PII = request.args.get('PII')
    TMAX = request.args.get('TMAX')
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
    R1 = request.args.get('R1')
    R2 = request.args.get('R2')
    R3 = request.args.get('R3')

    # return if has no arguments
    if(POP == None or PII == None or TMAX == None or IP == None or DMI == None or FM == None or FS == None or FC == None or TMC == None or T_UTI_D == None or DH == None or B1 == None or B2 == None or B3 == None or R1 == None or R2 == None or R3 == None):
        return 'Missing arguments: {POP, PII, TMAX, IP, DMI, FM, FS, FC, TMC, T_UTI_D, DH, B1, B2, B3, R1, R2, R3}'

    # predict
    #slon, slonSlow = predict_progression_slow(8843000, 1, 365, 5, 10, 0.8, 0.15, 0.05, 0.02, 7, 11, 0.33, 0.01, 0.01, 0.33, 0.00, 0.00)
    slon, slonSlow = predict_progression_slow(
        POP, PII, TMAX, IP, DMI, FM, FS, FC, TMC, T_UTI_D, DH, B1, B2, B3, R1, R2, R3)

    # json
    json_list = get_predict_json_progression_slow(slon, slonSlow)

    # return
    return jsonify(json_list)


### Main ###
if __name__ == "__main__":
    app.run()
    #app.run(host='10.110.21.13', port=3012)
