package io.github.aemiroo.cosmeticpets;

public enum PetKind {
    CAT("Cat"), BAT("Bat"), ZOMBIE("Zombie"), GHOST("Ghost"), PUMPKIN("Pumpkin"), SNOWMAN("Snowman"), REINDEER("Reindeer");
    boolean modelled() { return this == GHOST || this == PUMPKIN || this == SNOWMAN || this == REINDEER; }
    final String label;
    PetKind(String label) { this.label = label; }
}
