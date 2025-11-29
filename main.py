from flask import Flask, jsonify, Response
from flask_cors import CORS
import cv2
import time
from cv_layer import run_cv_models
from agent_layer import agent_decision
from alert_layer import send_sms_alert

app = Flask(__name__)
CORS(app)

print("🔥 Starting Women Safety AI Backend...")

camera = cv2.VideoCapture(0)

# Global State
current_state = {
    "women": 0, "men": 0, "sos": False,
    "scene": "Initializing...", "risk": 0, "decision": "Safe"
}

# SMS Cooldown (prevent spamming)
last_sms_time = 0
SMS_COOLDOWN = 30 

def generate_frames():
    global current_state, last_sms_time
    
    while True:
        success, frame = camera.read()
        if not success: break
        
        try:
            # 1. Run AI
            cv_data = run_cv_models(frame)
            current_state.update(cv_data)
            
            # 2. Risk Analysis
            scene, decision, risk = agent_decision({
                "women": cv_data['women'],
                "men": cv_data['men'],
                "sos_gesture": cv_data['sos']
            })
            current_state["risk"] = risk
            current_state["decision"] = decision

            # 3. Alerts
            if cv_data['sos'] and (time.time() - last_sms_time > SMS_COOLDOWN):
                print("🚨 SOS TRIGGERED - SENDING SMS...")
                send_sms_alert(f"🚨 SOS ALERT! A woman needs help. Risk Level: {risk}")
                last_sms_time = time.time()

            # 4. Draw Overlay
            color = (0, 255, 0)
            if risk > 0.7: color = (0, 0, 255)
            
            cv2.putText(frame, f"Risk: {risk} | {decision}", (20, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            if cv_data['sos']:
                 cv2.putText(frame, "SOS DETECTED!", (20, 100), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        except Exception as e:
            pass # Keep streaming even if error

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/process')
def process():
    return jsonify(current_state)

if __name__ == "__main__":
    app.run(debug=True, port=5000)