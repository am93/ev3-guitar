package reciever;

import org.eclipse.paho.client.mqttv3.*;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;

import java.util.Arrays;
import java.util.concurrent.ConcurrentLinkedQueue;

public class MqttCommunicator implements MqttCallback {

    // Connection related parameters
    private final int QOS = 0;
    private final String MQTT_TOPIC = "sound_data";
    private final String MQTT_BROKER = "tcp://127.0.0.1:10042"; //"tcp://192.168.0.102:10042"
    private final String CLIENT_ID = "MAIN_STATION";

    // instance of mqtt client
    private MqttClient client = null;

    // data queue
    private ConcurrentLinkedQueue<Integer[]> dataQueue;

    // constructor
    public MqttCommunicator()
    {
        // initialize queue
        dataQueue = new ConcurrentLinkedQueue<Integer[]>();

        MqttConnectOptions opts = new MqttConnectOptions();
        opts.setCleanSession(true);

        // client initialization
        try {
            this.client = new MqttClient(MQTT_BROKER, CLIENT_ID, new MemoryPersistence());
            System.out.println("Client initialized !");
        } catch (MqttException e) {
            System.out.println("Client creation failed: "+e.getMessage());
        }

        client.setCallback(this);

        // client connection
        try {
            this.client.connect(opts);
            System.out.println("Connected to "+MQTT_BROKER+" !");
        } catch (MqttException e) {
            System.out.println("Client connection failed: "+e.getMessage());
        }

        // client subscription
        try {
            client.subscribe(MQTT_TOPIC);
            System.out.println("Subscribed to topic: "+MQTT_TOPIC);
        } catch (MqttException e) {
            System.out.println("Client subscription failed: "+e.getMessage());
        }
    }

    /**
     * Callback to be triggered on connection lost.
     * @param throwable cause
     */
    public void connectionLost(Throwable throwable) {
        System.out.println("Connection with broker lost: "+throwable.getMessage());
        System.exit(1);
    }

    /**
     * Callback to be called on message arrival.
     * @param topic source of message
     * @param msg recieved payload
     * @throws Exception
     */
    public void messageArrived(String topic, MqttMessage msg) throws Exception {

        String payload = new String(msg.getPayload());
        Integer[] values =  Arrays.stream(payload.split(";")).map(x -> Integer.parseInt(x)).toArray(Integer[]::new);
        dataQueue.add(values);

    }

    public void deliveryComplete(IMqttDeliveryToken iMqttDeliveryToken) {
        // This should be never called, because we have QOS = 0, it has to be implemented becasue of interface !
    }

    /**
     * This function should be called to obtain data from queue.
     * @return Integer[] or null if queue is empty
     */
    public Integer[] getQueueData()
    {
        return dataQueue.isEmpty() ? null : dataQueue.poll();
    }
}
