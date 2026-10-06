package io.github.aemiroo.cosmeticpets;

public enum PetKind {
    CAT("Cat"), BAT("Bat"), ZOMBIE("Zombie");
    final String label;
    PetKind(String label) { this.label = label; }
}
