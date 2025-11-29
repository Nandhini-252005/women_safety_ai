def compute_risk(women, men, sos):
    risk = 0.0

    if sos:
        risk += 0.7

    if women == 1 and men >= 1:
        risk += 0.2

    if men > women:
        risk += 0.15

    return min(1.0, round(risk, 2))
