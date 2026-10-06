package io.github.aemiroo.cosmeticpets;

public enum PetKind {
    CAT("Cat"), BAT("Bat"), ZOMBIE("Zombie"), GHOST("Ghost"), PUMPKIN("Pumpkin");
    boolean modelled() { return this == GHOST || this == PUMPKIN; }
    final String label;
    PetKind(String label) { this.label = label; }
}
