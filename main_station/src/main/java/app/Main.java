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
        // electric guitar (overdriven)
        channel.programChange(29);

        System.out.println("Ready");

        GuitarEvent oldEvent = new GuitarEvent();

        while (true) {
            Integer[] receive;
            while((receive = communicator.getQueueData()) == null);

            System.out.printf("%d;%d;%d -> ", receive[0], receive[1], receive[2]);
            GuitarEvent event = new GuitarEvent(receive[0], receive[1], receive[2]);
            System.out.println(event.toString());

            if (event.played && !event.equals(oldEvent) && event.note != GuitarEvent.Note.ERROR) {
                channel.allNotesOff();
                int midiNumber = event.note.midiNumber + (event.isArmRaised ? GuitarEvent.OCTAVE_MODIFIER : 0);
                channel.noteOn(midiNumber, 120);
            } else if (!event.equals(oldEvent)) {
                channel.allNotesOff();
            }
            oldEvent = event;
        }
    }

    public static void main(String[] args) {
        new Main().run();
    }
}
