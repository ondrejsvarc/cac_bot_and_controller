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
        "target_id": target_id,
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
        target = payload.get("target_id")
        if target != CONTROLLER_ID:
            return

        sender = payload.get("sender_id")
        print(f"Received message from {sender}:\n{msg.payload.decode()}")

    except json.JSONDecodeError:
        print("Received non-JSON message")
    except Exception as e:
        print(f"Error processing message: {e}")


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
                send_command(client, target_id, cmd)

        client.loop_stop()
    except KeyboardInterrupt:
        print("Stopping...")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()
