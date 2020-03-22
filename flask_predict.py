import numpy as np
import pandas as pd
from scipy.integrate import odeint
import json
import flask
from flask import request, jsonify
from flask import Flask


def seir(y, t, b, a, g, p, u, N):
    dy = [0, 0, 0, 0, 0, 0]
    S = N-sum(y)
    dy[0] = np.dot(b[1:3], y[1:3])*S-a*y[0]  # E
    dy[1] = a*y[0]-(g[1]+p[1])*y[1]  # I1
    dy[2] = p[1]*y[1] - (g[2]+p[2])*y[2]  # I2
    dy[3] = p[2]*y[2] - (g[3]+u)*y[3]  # I3
    dy[4] = np.dot(g[1:3], y[1:3])  # R
    dy[5] = u*y[3]  # D

    return dy


def predict(IP, DMI, FM, FS, FC, TMC, T_UTI_D, DH, CHNT, POP, TMAX):

    # --- Parametros de entrada
    # IP - Periodo de incubação em dias
    IP = int(IP)
    # DMI - Duracao de infecções leves em dias
    DMI = float(DMI)
    # FM - Fracao de infeccoes leves
    FM = float(FM)
    # FS - Fracao de infeccoes graves
    FS = float(FS)
    # FC - Fracao de infeccoes criticas
    FC = float(FC)
    # TMC - Taxa de mortalidade de casos (fracao de infeccoes resultando em morte)
    TMC = float(TMC)
    # T_UIT_D - Tempo de internacao na UTI ate a morte em dias
    T_UTI_D = int(T_UTI_D)
    # DH - Duracao da internacao no hospital em dias
    DH = int(DH)
    # CHNT - Casos hospitalizados nao transmitem
    CHNT = int(1)
    # POP - Tamanho da populacao
    POP = int(POP)
    # TMAX - Tempo de medicao em dias
    TMAX = int(TMAX)

    # Soma de FM, FS e FC deve ser igual a 1
    if(FM+FS+FC != 1):
        return -1

    # --- Definir parametros e executar ODE
    b = np.zeros(4)  # beta
    g = np.zeros(4)  # gamma
    p = np.zeros(3)
    a = 1/IP
    u = (1/T_UTI_D)*(TMC/FC)
    g[3] = (1/T_UTI_D)-u
    p[2] = (1/DH)*(FC/(FC+FS))
    g[2] = (1/DH)-p[2]
    g[1] = (1/DMI)*FM
    p[1] = (1/DMI)-g[1]

    if(CHNT != 0):
        # casos hospitalizados nao transmitem
        b = 2.5e-4*np.array([0, 1, 0, 0])
    else:
        # todas as etapas transmitem igualmente
        b = 2.5e-4*np.array([1, 1, 1, 1])

    # Calcula a taxa reprodutiva basica
    R0 = POP*((b[1]/(p[1]+g[1]))+(p[1]/(p[1]+g[1])) *
              (b[2]/(p[2]+g[2]) + (p[2]/(p[2]+g[2]))*(b[3]/(u+g[3]))))

    # --- Aplicar predicao

    tvec = np.arange(0, TMAX, 0.1)
    ic = np.zeros(6)
    ic[0] = 1

    soln = odeint(seir, ic, tvec, args=(b, a, g, p, u, POP))
    soln = np.hstack((POP-np.sum(soln, axis=1, keepdims=True), soln))

    # soln -> [0:TMAX][S, E, I1, I2, I3, R, D]
    return soln


def get_predict_json(soln):
    json_list = []
    for n in soln:
        json_dict = json.dumps(
            {'S': n[0], 'E': n[1], 'I1': n[2], 'I2': n[3], 'I3': n[4], 'R': n[5], 'D': n[6]})
        json_list.append(json.loads(json_dict))
    return json_list


################################## Flask Configs ###############################
app = flask.Flask(__name__)
app.config["DEBUG"] = False

################################## Flask Services ##############################
# http://lapisco.fortaleza.ifce.edu.br:3012/api/covid19predict?IP=5&DMI=10&FM=0.8&FS=0.15&FC=0.05&TMC=0.02&T_UTI_D=7&DH=11&CHNT=1&POP=8843000&TMAX=365
@app.route('/api/covid19predict', methods=['GET'], endpoint='apicovid19predict')
def apicovid19predict():
    # params
    IP = request.args.get('IP')
    DMI = request.args.get('DMI')
    FM = request.args.get('FM')
    FS = request.args.get('FS')
    FC = request.args.get('FC')
    TMC = request.args.get('TMC')
    T_UTI_D = request.args.get('T_UTI_D')
    DH = request.args.get('DH')
    CHNT = request.args.get('CHNT')
    POP = request.args.get('POP')
    TMAX = request.args.get('TMAX')

    # return if has no arguments
    if(IP == None or DMI == None or FM == None or FS == None or FC == None or TMC == None or T_UTI_D == None or DH == None or CHNT == None or POP == None or TMAX == None):
        return '<h2 style="text-align: center;"><strong>covid19predict (routes)</strong></h2><ul><li><strong>predict - api/covid19predict?</strong></li><li><strong>input information - <a href="http://lapisco.fortaleza.ifce.edu.br:3012/api/covid19predict/input">api/covid19predict/input</a></strong></li><li><strong>output information - <a href="http://lapisco.fortaleza.ifce.edu.br:3012/api/covid19predict/output">api/covid19predict/output</a></strong></li></ul>'

    # predict
    #slon = predict(5, 10, 0.8, 0.15, 0.05, 0.02, 7, 11, 1, 8843000, 365)
    slon = predict(IP, DMI, FM, FS, FC, TMC, T_UTI_D, DH, CHNT, POP, TMAX)

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


################################## Main #######################################
if __name__ == "__main__":
    app.run()
    #app.run(host='10.110.21.13', port=3012)
