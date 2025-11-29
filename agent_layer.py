def agent_decision(behavior):
    women = behavior.get("women", 0)
    men = behavior.get("men", 0)
    sos = behavior.get("sos_gesture", False)

    scene = f"{women} women, {men} men detected. SOS: {sos}"

    # Risk Logic
    if sos:
        risk = 1.0
        decision = "CRITICAL: SOS DETECTED"
    elif men > 0 and women == 1:
        # 1 Woman surrounded by men
        if men >= 3:
            risk = 0.9
            decision = "High Risk: Lone Woman + Group of Men"
        else:
            risk = 0.6
            decision = "Caution: Lone Woman"
    elif men > women:
        risk = 0.4
        decision = "Moderate Risk"
    else:
        risk = 0.1
        decision = "Safe"

    return scene, decision, round(risk, 2)