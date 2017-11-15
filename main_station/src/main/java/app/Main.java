package app;

import reciever.GuitarEvent;
import reciever.MqttCommunicator;
import javax.sound.midi.*;

public class Main {

    private void run() {
        MqttCommunicator communicator = new MqttCommunicator();

        Synthesizer synth;

        try {
            synth = MidiSystem.getSynthesizer();
            synth.open();
        } catch (MidiUnavailableException e) {
            e.printStackTrace();
            return;
        }

        MidiChannel channel = synth.getChannels()[0];

        System.out.println("Ready");

        GuitarEvent oldEvent = new GuitarEvent();

        while (true) {
            Integer[] receive;
            while((receive = communicator.getQueueData()) == null);

            System.out.printf("%d;%d;%d: ", receive[0], receive[1], receive[2]);
            GuitarEvent event = new GuitarEvent(receive[0], receive[1], receive[2]);
            System.out.println(event.toString());

            if (event.equals(oldEvent) || event.note == GuitarEvent.Note.ERROR) {
                continue;
            }

            channel.allNotesOff();
            if (event.picked) {
                channel.noteOn(event.note.midiNumber, 120);
            }
        }
    }

    public static void main(String[] args) {
        new Main().run();
    }
}
