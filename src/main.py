#!/usr/bin/python3
import messenger

if __name__ == "__main__": # pragma: no cover
    mqttConnection = messenger.Messenger()
    if not mqttConnection.connect():
        print("No MQTT broker running")
        quit()

    mqttConnection.foreverLoop()
    
    #stop mqtt
    mqttConnection.disconnect()