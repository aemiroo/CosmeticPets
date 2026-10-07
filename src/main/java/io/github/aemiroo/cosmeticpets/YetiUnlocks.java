package io.github.aemiroo.cosmeticpets;
import java.io.IOException;
import java.nio.file.*;
import java.util.*;
import org.bukkit.configuration.InvalidConfigurationException;
import org.bukkit.configuration.file.YamlConfiguration;

final class YetiUnlocks {
    private final Path file;
    private final Set<UUID> unlocked=new HashSet<>();
    YetiUnlocks(Path file) throws IOException {
        this.file=file;
        if(!Files.exists(file))return;
        var yaml=new YamlConfiguration();
        try { yaml.load(file.toFile()); }
        catch(InvalidConfigurationException ex) { throw new IOException("Invalid yeti-unlocks.yml",ex); }
        if(yaml.contains("players")&&!yaml.isList("players"))throw new IOException("Invalid Yeti unlock list");
        for(String value:yaml.getStringList("players")) {
            try { unlocked.add(UUID.fromString(value)); }
            catch(IllegalArgumentException ex) { throw new IOException("Invalid Yeti unlock UUID",ex); }
        }
    }
    boolean contains(UUID id) { return unlocked.contains(id); }
    void grant(UUID id) throws IOException {
        Objects.requireNonNull(id);
        if(unlocked.contains(id))return;
        var next=new HashSet<>(unlocked);next.add(id);
        var yaml=new YamlConfiguration();
        yaml.set("players",next.stream().map(UUID::toString).sorted().toList());
        Path parent=file.toAbsolutePath().getParent();Files.createDirectories(parent);
        Path temp=Files.createTempFile(parent,"yeti-unlocks-",".tmp");
        try {
            yaml.save(temp.toFile());
            try { Files.move(temp,file,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING); }
            catch(AtomicMoveNotSupportedException ex) { Files.move(temp,file,StandardCopyOption.REPLACE_EXISTING); }
            unlocked.clear();unlocked.addAll(next);
        } finally { Files.deleteIfExists(temp); }
    }
}
