package io.github.aemiroo.cosmeticpets;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import static org.junit.jupiter.api.Assertions.*;
import java.nio.file.*;
import java.util.UUID;
import java.io.IOException;
class YetiUnlocksTest {
    @TempDir Path directory;
    @Test void grantSurvivesRestartAndIsIdempotent() throws Exception {
        Path file=directory.resolve("yeti-unlocks.yml");UUID id=UUID.randomUUID();
        var first=new YetiUnlocks(file);assertFalse(first.contains(id));
        first.grant(id);String saved=Files.readString(file);first.grant(id);
        assertEquals(saved,Files.readString(file));
        assertTrue(new YetiUnlocks(file).contains(id));
        assertFalse(new YetiUnlocks(file).contains(UUID.randomUUID()));
    }
    @Test void malformedStoreFailsClosed() throws Exception {
        Path file=directory.resolve("yeti-unlocks.yml");Files.writeString(file,"players: [not-a-uuid]");
        assertThrows(IOException.class,()->new YetiUnlocks(file));
        Files.writeString(file,"players: wrong-type");
        assertThrows(IOException.class,()->new YetiUnlocks(file));
    }
}
