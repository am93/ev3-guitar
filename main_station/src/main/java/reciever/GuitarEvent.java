package reciever;

/**
 * Represents a guitar event sent from EV3.
 * Contains info about note height, pick action and arm position.
 *
 * @author Jure Jesensek
 */
public class GuitarEvent {

    /**
     * Enums containing an octave of notes (from C5 to C6) and their corresponding MIDI number.
     * <p />
     * Uses "english" notation concerning B/H note: C, C#, D, D#, E, F, F#, G, G#, A, <b>A#</b>,
     * <b>B</b>, C.
     */
    public enum Note {

        /** C5. */
        C5(60),
        /** C#5. */
        Csh5(61),
        /** D5. */
        D5(62),
        /** D#5. */
        Dsh5(63),
        /** E5. */
        E5(64),
        /** F5. */
        F5(65),
        /** F#5. */
        Fsh5(66),
        /** G5. */
        G5(67),
        /** G#5. */
        Gsh5(68),
        /** A5. */
        A5(69),
        /** A#5 (English notation). */
        Ash5(70),
        /** B5 (English notation). */
        B5(71),
        /** C6. */
        C6(72),
        /** Error note. */
        ERROR(-1);

        /** MIDI number. */
        public final int midiNumber;

        Note(int value) {
            this.midiNumber = value;
        }
    }

    public final Note note;
    public final boolean picked;
    public final boolean isArmRaised;

    private static final int PICKED = 0;

    private static final int NECK_HIGHEST_POSITION = 0;
    private static final int NECK_LOWEST_POSITION = 69;

    private static final int ARM_LOWEST_POSITION = 60;
    private static final int ARM_HIGHEST_POSITION = 0;

    public GuitarEvent() {
        this.note = Note.ERROR;
        this.picked = false;
        this.isArmRaised = false;
    }

    public GuitarEvent(int distance, int picked, int armPosition) {
        if (distance < NECK_HIGHEST_POSITION) {
            distance = NECK_HIGHEST_POSITION;
        } else if (distance > NECK_LOWEST_POSITION) {
            distance = NECK_LOWEST_POSITION;
        }
        // TODO: 15.11.2017 change
        switch (distance / 9) {
            case 0: this.note = Note.C6; break;
            case 1: this.note = Note.B5; break;
            case 2: this.note = Note.A5; break;
            case 3: this.note = Note.G5; break;
            case 4: this.note = Note.F5; break;
            case 5: this.note = Note.E5; break;
            case 6: this.note = Note.D5; break;
            case 7: this.note = Note.C5; break;
            default: this.note = Note.ERROR;
        }
        this.picked = picked == PICKED;
        this.isArmRaised = armPosition > (ARM_LOWEST_POSITION - ARM_HIGHEST_POSITION) / 2;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (o == null || getClass() != o.getClass()) {
            return false;
        }

        GuitarEvent event = (GuitarEvent) o;

        if (picked != event.picked) {
            return false;
        }
        if (isArmRaised != event.isArmRaised) {
            return false;
        }
        return note == event.note;
    }

    @Override
    public String toString() {
        return note + ", " + (picked ? "" : "not ") + "picked, " + (isArmRaised ? "raised" : "");
    }
}
