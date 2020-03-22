import numpy as np
import pandas as pd
from scipy.integrate import odeint


def taxa_reprodutiva(N, b, p, g, u):
    return N*b[0]/(p[1]+g[0]) + (p[0]/(p[0]+g[0]))*(N*b[1]/(p[1]+g[1]) + N*b[2]*p[1]/((p[1]+g[1])*(u + g[2])))


def params(g, p, IncubPeriod, FracMild, FracCritical, FracSevere, TimeICUDeath, CFR, DurMildInf, DurHosp, tmax, i):

    a = 1/IncubPeriod  # Taxa de transição dos expostos para infectado

    if FracCritical == 0:
        u = 0
    else:
        u = (1/TimeICUDeath)*(CFR/FracCritical)

    g[0] = (1/DurMildInf)*FracMild  # Taxa de recuperação I1
    p[0] = (1/DurMildInf)-g[0]  # Taxa de progreção I1

    g[2] = (1/TimeICUDeath)-u  # Taxa de recuperação I3

    # Taxa de progressão I2
    p[1] = (1/DurHosp)*(FracCritical/(FracCritical+FracSevere))
    g[1] = (1/DurHosp)-p[1]  # Taxa de recuperação de I2

    tvec = np.arange(0, tmax, 0.1)
    # Inicia vetor da população (cada índice para cada tipo de infectado, exposto, etc)
    ic = np.zeros(6)
    ic[0] = i  # População sucetível = tamanho da população

    return a, u, g, p, tvec, ic


def seir(y, t, b, a, g, p, u, N):

    dy = [0, 0, 0, 0, 0, 0]
    S = N-sum(y)  # S -> casos sucetiveis
    dy[0] = (b[0]*y[1] + b[1]*y[2] + b[2]*y[3]) * \
        S - a*y[0]  # dE -> casos expostos
    dy[1] = a*y[0] - (g[0] + p[0])*y[1]  # dI1 -> Casos leves
    dy[2] = p[0]*y[1] - (g[1]+p[1])*y[2]  # dI2 -> Casos graves
    dy[3] = p[1]*y[2] - (g[2] + u)*y[3]  # dI3 -> Casos Críticos
    dy[4] = g[0]*y[1] + g[1]*y[2] + g[2]*y[3]  # dR -> Recuperados
    dy[5] = u*y[3]  # dD -> Mortos

    return dy


def growth_rate(tvec, soln, t1, t2, i):

    i1 = np.where(tvec == t1)[0][0]
    i2 = np.where(tvec == t2)[0][0]
    r = (np.log(soln[i2, 1])-np.log(soln[i1, 1]))/(t2-t1)
    DoublingTime = np.log(2)/r

    return r, DoublingTime


def predict_progression(POP, PII, TMAX, IP, DMI, FM, FS, FC, TMC, T_UTI_D, DH, B1, B2, B3):
    # --- Parametros de entrada
    # POP - Tamanho da populacao
    POP = int(POP)
    # PII - Pessoas inicialmente infectadas
    PII = int(PII)
    # TMAX - Tempo de medicao em dias
    TMAX = int(TMAX)
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
    # B1 - Taxa de transmissão - infecções leves
    B1 = float(B1)
    # B2 - Taxa de transmissão - infecções graves, relativa à infecção leve
    B2 = float(B2)
    # B3 - Taxa de transmissão - infecções críticas, relativa à infecção leve
    B3 = float(B3)

    # --- Definir parametros e executar ODE
    g = np.zeros(4)
    p = np.zeros(3)

    a, u, g, p, tvec, ic = params(
        g, p, IP, FM, FC, FS, T_UTI_D, TMC, DMI, DH, TMAX, PII)

    # Inicia vetor de taxa de transmissão
    B1 = B1/POP
    B2 = B2*B1
    B3 = B3*B1
    b = np.array([B1, B2, B3])

    # Simulacao
    soln = odeint(seir, ic, tvec, args=(b, a, g, p, u, POP))
    soln = np.hstack((POP-np.sum(soln, axis=1, keepdims=True), soln))

    # # Calcula a taxa reprodutiva básica
    # R0 = taxa_reprodutiva(POP, b, p, g, u)
    # # r - taxa de crescimento epidemico (por dia) | DoublingTime - Tempo de duplicacao (dias)
    # (r, DoublingTime) = growth_rate(tvec, soln, 10, 20, 1)

    # soln -> [0:TMAX][S, E, I1, I2, I3, R, D]
    return soln


def predict_progression_slow(POP, PII, TMAX, IP, DMI, FM, FS, FC, TMC, T_UTI_D, DH, B1, B2, B3, R1, R2, R3):
    # --- Parametros de entrada
    # # POP - Tamanho da populacao
    POP = int(POP)
    # PII - Pessoas inicialmente infectadas
    PII = int(PII)
    # TMAX - Tempo de medicao em dias
    TMAX = int(TMAX)
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
    # B1 - Taxa de transmissão - infecções leves
    B1 = float(B1)
    # B2 - Taxa de transmissão - infecções graves, relativa à infecção leve
    B2 = float(B2)
    # B3 - Taxa de transmissão - infecções críticas, relativa à infecção leve
    B3 = float(B3)
    # R1 - Redução em B1
    R1 = float(R1)
    # R2 - Redução em B2
    R2 = float(R2)
    # R3 - Redução em B3
    R3 = float(R3)

    # --- Definir parametros e executar ODE
    g = np.zeros(4)
    p = np.zeros(3)

    a, u, g, p, tvec, ic = params(
        g, p, IP, FM, FC, FS, T_UTI_D, TMC, DMI, DH, TMAX, PII)

    # Inicia vetor de taxa de transmissão
    B1 = B1/POP
    B2 = B2*B1
    B3 = B3*B1
    b = np.array([B1, B2, B3])
    bSlow = np.array([(1-R1)*B1, (1-R2)*B2, (1-R3)*B3])

    # Simulacao
    soln = odeint(seir, ic, tvec, args=(b, a, g, p, u, POP))
    soln = np.hstack((POP-np.sum(soln, axis=1, keepdims=True), soln))

    solnSlow = odeint(seir, ic, tvec, args=(bSlow, a, g, p, u, POP))
    solnSlow = np.hstack(
        (POP-np.sum(solnSlow, axis=1, keepdims=True), solnSlow))

    # # Calcula a taxa reprodutiva básica
    # R0 = taxa_reprodutiva(POP, b, p, g, u)
    # R0Slow = taxa_reprodutiva(N, bSlow, p, g, u)
    # # r - taxa de crescimento epidemico (por dia) | DoublingTime - Tempo de duplicacao (dias) (slow == com reducao)
    # (r, DoublingTime) = growth_rate(tvec, soln, 30, 40, 1)
    # (rSlow, DoublingTimeSlow) = growth_rate(tvec, solnSlow, 30, 40, i)

    # soln -> [0:TMAX][S, E, I1, I2, I3, R, D]
    return soln, solnSlow


def predict_hospital_capacity(POP, PII, TMAX, IP, DMI, FM, FS, FC, TMC, T_UTI_D, DH, B1, B2, B3, R1, R2, R3, L1, L2, P1, P2, P3):
    # --- Parametros de entrada
    # # POP - Tamanho da populacao
    POP = int(POP)
    # PII - Pessoas inicialmente infectadas
    PII = int(PII)
    # TMAX - Tempo de medicao em dias
    TMAX = int(TMAX)
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
    # B1 - Taxa de transmissão - infecções leves
    B1 = float(B1)
    # B2 - Taxa de transmissão - infecções graves, relativa à infecção leve
    B2 = float(B2)
    # B3 - Taxa de transmissão - infecções críticas, relativa à infecção leve
    B3 = float(B3)
    # R1 - Redução em B1
    R1 = float(R1)
    # R2 - Redução em B2
    R2 = float(R2)
    # R3 - Redução em B3
    R3 = float(R3)
    # L1 - Leitos Hospitalares disponíveis
    L1 = int(L1)
    # L2 - Leitos de UTI disponíveis
    L2 = int(L2)
    # P1 - Pacientes que podem ser ventilados em protocolos convencionais
    P1 = int(P1)
    # P2 - Pacientes que podem ser ventilados em protocolo de contingência
    P2 = int(P2)
    # P3 - Pacientes que podem ser ventilados em protocolo de crise
    P3 = int(P3)

    # --- Definir parametros e executar ODE
    g = np.zeros(4)
    p = np.zeros(3)

    a, u, g, p, tvec, ic = params(
        g, p, IP, FM, FC, FS, T_UTI_D, TMC, DMI, DH, TMAX, PII)

    # Inicia vetor de taxa de transmissão
    B1 = B1/POP
    B2 = B2*B1
    B3 = B3*B1
    b = np.array([B1, B2, B3])
    bSlow = np.array([(1-R1)*B1, (1-R2)*B2, (1-R3)*B3])

    # Simulacao
    soln = odeint(seir, ic, tvec, args=(b, a, g, p, u, POP))
    soln = np.hstack((POP-np.sum(soln, axis=1, keepdims=True), soln))

    solnSlow = odeint(seir, ic, tvec, args=(bSlow, a, g, p, u, POP))
    solnSlow = np.hstack(
        (POP-np.sum(solnSlow, axis=1, keepdims=True), solnSlow))

    # # Calcula a taxa reprodutiva básica
    # R0 = taxa_reprodutiva(POP, b, p, g, u)
    # R0Slow = taxa_reprodutiva(N, bSlow, p, g, u)
    # # r - taxa de crescimento epidemico (por dia) | DoublingTime - Tempo de duplicacao (dias) (slow == com reducao)
    # (r, DoublingTime) = growth_rate(tvec, soln, 30, 40, 1)
    # (rSlow, DoublingTimeSlow) = growth_rate(tvec, solnSlow, 30, 40, i)

    # soln -> [0:TMAX][S, E, I1, I2, I3, R, D]
    return soln, solnSlow
