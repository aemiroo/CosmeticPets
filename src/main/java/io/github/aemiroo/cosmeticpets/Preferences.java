package io.github.aemiroo.cosmeticpets;

import java.io.IOException;
import java.nio.file.*;
import java.util.*;
import org.bukkit.configuration.InvalidConfigurationException;
import org.bukkit.configuration.file.YamlConfiguration;

final class Preferences {
    record Choice(PetKind kind, boolean summoned) {}
    private final Path file;
    private final Map<UUID, Choice> choices = new HashMap<>();
    Preferences(Path file) throws IOException {
        this.file = file;
        if (!Files.exists(file)) return;
        YamlConfiguration yaml = new YamlConfiguration();
        try { yaml.load(file.toFile()); }
        catch (InvalidConfigurationException e) { throw new IOException("Invalid players.yml", e); }
        for (String key : yaml.getKeys(false)) {
            try {
                UUID id = UUID.fromString(key);
                PetKind kind = PetKind.valueOf(yaml.getString(key + ".pet", "").toUpperCase(Locale.ROOT));
                if (kind != PetKind.SNOWMAN && kind != PetKind.REINDEER && kind != PetKind.YETI) kind = PetKind.SNOWMAN;
                choices.put(id, new Choice(kind, yaml.getBoolean(key + ".summoned", false)));
            } catch (IllegalArgumentException e) { throw new IOException("Invalid pet preference", e); }
        }
    }
    Choice get(UUID id) { return choices.get(id); }
    void set(UUID id, Choice choice) throws IOException {
        var updated = new HashMap<>(choices);
        updated.put(id, choice);
        var yaml = new YamlConfiguration();
        updated.forEach((uuid, value) -> {
            yaml.set(uuid + ".pet", value.kind().name().toLowerCase(Locale.ROOT));
            yaml.set(uuid + ".summoned", value.summoned());
        });
        Files.createDirectories(file.toAbsolutePath().getParent());
        Path temporary = Files.createTempFile(file.toAbsolutePath().getParent(), "players-", ".tmp");
        try {
            yaml.save(temporary.toFile());
            try { Files.move(temporary, file, StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING); }
            catch (AtomicMoveNotSupportedException e) { Files.move(temporary, file, StandardCopyOption.REPLACE_EXISTING); }
            choices.clear(); choices.putAll(updated);
        } finally { Files.deleteIfExists(temporary); }
    }
}
