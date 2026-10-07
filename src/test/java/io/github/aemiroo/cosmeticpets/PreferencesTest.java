package io.github.aemiroo.cosmeticpets;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import java.nio.file.*;
import java.util.UUID;
import static org.junit.jupiter.api.Assertions.*;
class PreferencesTest {
    @TempDir Path directory;
    @Test void savesIndependentOwnersAndDismissedSelectionAcrossRestart() throws Exception {
        Path file = directory.resolve("players.yml");
        UUID one = UUID.randomUUID(), two = UUID.randomUUID();
        var store = new Preferences(file);
        store.set(one, new Preferences.Choice(PetKind.CAT, true));
        store.set(two, new Preferences.Choice(PetKind.BAT, true));
        store.set(one, new Preferences.Choice(PetKind.CAT, false));
        var reloaded = new Preferences(file);
        assertEquals(new Preferences.Choice(PetKind.SNOWMAN, false), reloaded.get(one));
        assertEquals(new Preferences.Choice(PetKind.SNOWMAN, true), reloaded.get(two));
        assertNull(reloaded.get(UUID.randomUUID()));
    }
    @Test void ghostChoiceSurvivesRestartAndDismissal() throws Exception {
        Path file = directory.resolve("players.yml");
        UUID owner = UUID.randomUUID();
        var store = new Preferences(file);
        store.set(owner, new Preferences.Choice(PetKind.GHOST, true));
        assertEquals(new Preferences.Choice(PetKind.SNOWMAN, true), new Preferences(file).get(owner));
        store.set(owner, new Preferences.Choice(PetKind.GHOST, false));
        assertEquals(new Preferences.Choice(PetKind.SNOWMAN, false), new Preferences(file).get(owner));
    }
    @Test void pumpkinSelectionSurvivesRestartAndDismissal() throws Exception {
        Path file = directory.resolve("players.yml");
        UUID owner = UUID.randomUUID();
        var store = new Preferences(file);
        store.set(owner, new Preferences.Choice(PetKind.PUMPKIN, true));
        assertEquals(new Preferences.Choice(PetKind.SNOWMAN, true), new Preferences(file).get(owner));
        store.set(owner, new Preferences.Choice(PetKind.PUMPKIN, false));
        assertEquals(new Preferences.Choice(PetKind.SNOWMAN, false), new Preferences(file).get(owner));
    }
    @Test void christmasSelectionsSurviveRestartAndDismissal() throws Exception {
        Path file=directory.resolve("players.yml");
        var store=new Preferences(file);
        for (PetKind kind : new PetKind[]{PetKind.SNOWMAN,PetKind.REINDEER}) {
            UUID owner=UUID.randomUUID();
            store.set(owner,new Preferences.Choice(kind,true));
            assertEquals(new Preferences.Choice(kind,true),new Preferences(file).get(owner));
            store.set(owner,new Preferences.Choice(kind,false));
            assertEquals(new Preferences.Choice(kind,false),new Preferences(file).get(owner));
        }
    }
    @Test void everyRetiredPetMigratesWithoutChangingSummonedState() throws Exception {
        Path file=directory.resolve("players.yml");
        for (PetKind kind : new PetKind[]{PetKind.CAT,PetKind.BAT,PetKind.ZOMBIE,PetKind.GHOST,PetKind.PUMPKIN}) {
            for (boolean summoned : new boolean[]{true,false}) {
                UUID owner=UUID.randomUUID();
                Files.writeString(file,owner+":\n  pet: "+kind.name().toLowerCase()+"\n  summoned: "+summoned+"\n");
                assertEquals(new Preferences.Choice(PetKind.SNOWMAN,summoned),new Preferences(file).get(owner));
            }
        }
    }
    @Test void invalidPreferenceFailsInsteadOfOverwritingSavedFile() throws Exception {
        Path file = directory.resolve("players.yml");
        String content = UUID.randomUUID() + ":\n  pet: dragon\n  summoned: true\n";
        Files.writeString(file, content);
        assertThrows(java.io.IOException.class, () -> new Preferences(file));
        assertEquals(content, Files.readString(file));
    }
}
