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
        assertEquals(new Preferences.Choice(PetKind.CAT, false), reloaded.get(one));
        assertEquals(new Preferences.Choice(PetKind.BAT, true), reloaded.get(two));
        assertNull(reloaded.get(UUID.randomUUID()));
    }
    @Test void ghostChoiceSurvivesRestartAndDismissal() throws Exception {
        Path file = directory.resolve("players.yml");
        UUID owner = UUID.randomUUID();
        var store = new Preferences(file);
        store.set(owner, new Preferences.Choice(PetKind.GHOST, true));
        assertEquals(new Preferences.Choice(PetKind.GHOST, true), new Preferences(file).get(owner));
        store.set(owner, new Preferences.Choice(PetKind.GHOST, false));
        assertEquals(new Preferences.Choice(PetKind.GHOST, false), new Preferences(file).get(owner));
    }
    @Test void invalidPreferenceFailsInsteadOfOverwritingSavedFile() throws Exception {
        Path file = directory.resolve("players.yml");
        String content = UUID.randomUUID() + ":\n  pet: dragon\n  summoned: true\n";
        Files.writeString(file, content);
        assertThrows(java.io.IOException.class, () -> new Preferences(file));
        assertEquals(content, Files.readString(file));
    }
}
