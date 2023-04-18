import paho.mqtt.client as mqtt
import json
from multiprocessing import Process, Queue
import paho.mqtt.subscribe as subscribe
import paho.mqtt.publish as publish
import os

class Messenger():
    def __init__(self):
        self.connected = False
        self.mailAddress = None

        #aufbau der MQTT-Verbindung
        self.mqttConnection = mqtt.Client()

        self.mqttConnection.on_connect = self.__onConnectMQTT
        self.mqttConnection.on_message = self.__onMessageMQTT

        self.mqttConnection.message_callback_add("stt", self.__sttMQTTCallback)
        self.mqttConnection.message_callback_add("car/connected", self.__carConnectionCallback)

    def connect(self):
        if not self.connected:
            try:
                docker_container = os.environ.get('DOCKER_CONTAINER', False)
                if docker_container:
                    mqtt_address = "broker"
                else:
                    mqtt_address = "localhost"
                self.mqttConnection.connect(mqtt_address,1883,60)
            except:
                return False
            self.mqttConnection.loop_start()
        self.connected = True
        return True
    
    def disconnect(self):
        if self.connected:
            self.connected = False
            self.mqttConnection.loop_stop()
            self.mqttConnection.disconnect()
        return True
    
    def __onConnectMQTT(self, client, userdata, flags, rc):
        client.subscribe([("car/connected",0), ("stt",0)])

    def __sttMQTTCallback(self,client, userdata, msg):
        # Gather stt data
        try:
            sttData = json.loads(str(msg.payload.decode("utf-8")))
        except:
            print("Can't decode message")
            return(False)

        activation_nouns = ["nachricht", "artikel"]
        location_modifier = ["lokal"]
        length_modifier_long = ['lang']

        #check if stt  for this use case
        if intersection(sttData["nouns"], activation_nouns):
            # Make Request Response to location service if needed
            location = {}
            if intersection(sttData["adj"], location_modifier):
                queue = Queue()
                process = Process(target = mqttRequestResponseProzess, args = (queue, "req/location/current", None, "location/current"))
                process.start()
                process.join(timeout = 15)
                process.terminate()
                if process.exitcode == 0:
                    try:
                        location = json.loads(str(queue.get(timeout = 1).decode("utf-8")))
                    except:
                        print("Can't decode location answer")
                        return(False)
                else:
                    print("Location service terminated unsucessfully")
                    return(False)
            
            # Make Request Response to news service and activate tts
            queue = Queue()
            newsRequestPayload = {
                'numArticles': 1,
                'location': location
            }
            process = Process(target = mqttRequestResponseProzess, args = (queue, "req/news", json.dumps(newsRequestPayload), "news/article"))
            process.start()
            process.join(timeout = 15)
            process.terminate()

            if process.exitcode == 0:
                try:
                    newsData = json.loads(str(queue.get(timeout = 1).decode("utf-8")))
                except:
                    print("Can't decode news request answer")
                    return(False)

                if intersection(sttData["adv"], length_modifier_long):
                    if('text' in newsData):
                        self.mqttConnection.publish("tts", newsData['text'])
                else:
                    if('summary' in newsData):
                        self.mqttConnection.publish("tts", newsData['summary'])
                        q = Queue()
                        process = Process(target=mqttRequestResponseProzess, args=(q,"tts","Sag ja falls du mehr wissen willst?","stt"))
                        process.start()
                        process.join(timeout=15)
                        process.terminate()
                        if process.exitcode == 0:
                            try:
                                mqttData = q.get(timeout=1)
                            except:
                                return(False)

                            try:
                                mqttData = json.loads(str(mqttData.decode("utf-8")))
                            except:
                                print("Can't decode message")
                                return(False)

                            for value in mqttData["tokens"]:
                                if value["token"] == "ja":
                                    self.mqttConnection.publish("tts", newsData['text'])
                                    break

            else:
                print("News service terminated unsucessfully")
                return(False)


    #received default mqtt messages
    def __onMessageMQTT(self, client, userdata, msg):
        pass

    def foreverLoop(self):
        self.mqttConnection.loop_forever()

    def __carConnectionCallback(self, client, userdata, msg):
        self.mqttConnection.publish("tts", "Du bist mit deinem Auto verbunden. Hier eine lokale Nachricht")        
        
        # Make Request Response to location service
        queue = Queue()
        process = Process(target = mqttRequestResponseProzess, args = (queue, "req/location/current", None, "location/current"))
        process.start()
        process.join(timeout = 15)
        process.terminate()
        if process.exitcode == 0:
            try:
                location = json.loads(str(queue.get(timeout = 1).decode("utf-8")))
            except:
                print("Can't decode location answer")
                return(False)
        else:
            print("Location service terminated unsucessfully")
            return(False)

        # Make Request Response to news service
        queue = Queue()
        newsRequestPayload = {
            'numArticles': 1,
            'location': location
        }
        process = Process(target = mqttRequestResponseProzess, args = (queue, "req/news", newsRequestPayload, "news/article"))
        process.start()
        process.join(timeout = 15)
        process.terminate()

        if process.exitcode == 0:
            try:
                newsData = json.loads(str(queue.get(timeout = 1).decode("utf-8")))
            except:
                print("Can't decode news request answer")
                return(False)
            if('summary' in newsData):
                self.mqttConnection.publish("tts", newsData['summary'])  
        else:
            print("News service terminated unsucessfully")
            return(False)

def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3

def mqttRequestResponseProzess(q, requestTopic, requestData, responseTopic):
    docker_container = os.environ.get('DOCKER_CONTAINER', False)
    if docker_container:
        mqtt_address = "broker"
    else:
        mqtt_address = "localhost"

    if requestData is None:
        publish.single(requestTopic,hostname=mqtt_address,port=1883)
    else:
        publish.single(requestTopic,payload=requestData,hostname=mqtt_address,port=1883)
    mqttResponse = subscribe.simple(responseTopic,hostname=mqtt_address,port=1883).payload
    q.put(mqttResponse)