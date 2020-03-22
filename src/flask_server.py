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

# http://lapisco.fortaleza.ifce.edu.br:3012/api/covid19predict/input
@app.route('/api/covid19predict/input', methods=['GET'], endpoint='apicovid19predict_input')
def apicovid19predict_input():
    return '<h2 style="text-align: center;"><strong>covid19predict (input)</strong></h2><div><ul><li><strong>Per&iacute;odo de incuba&ccedil;&atilde;o em dias</strong> (IP)</li><li><strong>Dura&ccedil;&atilde;o de infec&ccedil;&otilde;es leves em dias</strong> (DMI)</li><li><strong>Fra&ccedil;&atilde;o de infec&ccedil;&otilde;es leves</strong> (FM)</li><li><strong>Fra&ccedil;&atilde;o de infec&ccedil;&otilde;es graves</strong> (FS)</li><li><strong>Fra&ccedil;&atilde;o de infec&ccedil;&otilde;es cr&iacute;ticas</strong> (FC)</li><li><strong>Taxa de mortalidade de casos - fra&ccedil;&atilde;o deinfec&ccedil;&otilde;es resultando em morte</strong> (TMC)</li><li><strong>Tempo de interna&ccedil;&atilde;o na UTI at&eacute; a morte em dias</strong> (T_UIT_D)</li><li><strong>Dura&ccedil;&atilde;o da interna&ccedil;&atilde;o no hospital em dias</strong> (DH)</li><li><strong>Tamanho da popula&ccedil;&atilde;o </strong>(POP)</li><li><strong>Tempo de medi&ccedil;&atilde;o em dias</strong> (TMAX)</li></ul><p><strong>Exemplo</strong>:&nbsp;<a href="http://lapisco.fortaleza.ifce.edu.br:3012/api/covid19predict?IP=5&amp;DMI=10&amp;FM=0.8&amp;FS=0.15&amp;FC=0.05&amp;TMC=0.02&amp;T_UTI_D=7&amp;DH=11&amp;CHNT=1&amp;POP=8843000&amp;TMAX=365">http://lapisco.fortaleza.ifce.edu.br:3012/api/covid19predict?IP=5&amp;DMI=10&amp;FM=0.8&amp;FS=0.15&amp;FC=0.05&amp;TMC=0.02&amp;T_UTI_D=7&amp;DH=11&amp;CHNT=1&amp;POP=8843000&amp;TMAX=365</a></p></div>'

# http://lapisco.fortaleza.ifce.edu.br:3012/api/covid19predict/output
@app.route('/api/covid19predict/output', methods=['GET'], endpoint='apicovid19predict_output')
def apicovid19predict_output():
    return '<h2 style="text-align: center;"><strong>covid19predict (output)</strong></h2><div><ul><li><strong>Indiv&iacute;duos Suscet&iacute;veis</strong> (S)</li><li><strong>Indiv&iacute;duos Expostos - infectados, mas ainda n&atilde;o infecciosos ou sintom&aacute;ticos</strong> (E);</li><li><strong>Indiv&iacute;duos infectados por classe de gravidade. A gravidade aumenta e assumimos que os indiv&iacute;duos devem passar por todas as classes anteriores</strong>:<ul><li><strong>Infec&ccedil;&atilde;o leve - hospitaliza&ccedil;&atilde;o n&atilde;o &eacute; necess&aacute;ria - Mild Infection</strong> (I1);</li><li><strong>Infec&ccedil;&atilde;o grave - hospitaliza&ccedil;&atilde;o necess&aacute;ria - Severe infection</strong> (I2);</li><li><strong>Infec&ccedil;&atilde;o critica - cuidados na UTI necess&aacute;ria - Critical infection</strong> (I3);</li></ul></li><li><strong>Indiv&iacute;duos que se recuperaram da doen&ccedil;a e agora est&atilde;o imunes</strong> (R);</li><li><strong>Indiv&iacute;duos mortos</strong> (D).</li></ul><p><strong>OBS.: N = S + E+ I1 + I2 + I3 + R + D (Tamanho total da popula&ccedil;&atilde;o)</strong></p></div>'


### Main ###
if __name__ == "__main__":
    app.run()
    #app.run(host='10.110.21.13', port=3012)
