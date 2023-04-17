from src import messenger
from unittest.mock import patch, ANY, MagicMock
from multiprocessing import Queue

def test_connect():
    obj = messenger.Messenger()
    with patch.object(obj, 'mqttConnection') as mock_connect:
        obj.connect()
        mock_connect.connect.assert_called_with("localhost",1883,60)

def test_disconnect():
    obj = messenger.Messenger()
    with patch.object(obj, 'connected', True), patch.object(obj, 'mqttConnection') as mock_connect:
        obj.disconnect()
        mock_connect.disconnect.assert_called()

def test_foreverLoop():
    obj = messenger.Messenger()
    with patch.object(obj, 'mqttConnection') as mock_connect:
        obj.foreverLoop()
        mock_connect.loop_forever.assert_called()

def test_onMQTTconnect():
    obj = messenger.Messenger()
    mock_client = MagicMock()
    obj._Messenger__onConnectMQTT(mock_client,None,None,None)
    mock_client.subscribe.assert_called_with([("car/connected",0), ("stt",0)])

def test_onMQTTMessage():
    obj = messenger.Messenger()
    obj._Messenger__onMessageMQTT(MagicMock(),None,None)

@patch("paho.mqtt.publish.single")
@patch("paho.mqtt.subscribe.simple")
def test_mqttRequestResponseProzess(mock_sub,mock_pub):
    mock_sub.return_value = type('obj', (object,), {'payload' : 'asdf'})
    messenger.mqttRequestResponseProzess(Queue(),"test/request","asdf","test/response")
    mock_pub.assert_called_with("test/request",payload="asdf",hostname=ANY,port=ANY)
    mock_sub.assert_called_with("test/response",hostname=ANY,port=ANY)

def test_intersection():
    assert messenger.intersection(["asdf","1234"],["jklö"]) == []
    assert messenger.intersection(["asdf","1234"],["asdf"]) == ["asdf"]