def generate_scene_text(b):
    return (
        f"{b['women']} women and {b['men']} men detected. "
        f"SOS: {b['sos_gesture']}. "
        f"Risk Level: {b['risk']}."
    )
