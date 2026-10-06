package io.github.aemiroo.cosmeticpets;

import com.github.retrooper.packetevents.PacketEvents;
import com.github.retrooper.packetevents.protocol.entity.data.EntityData;
import com.github.retrooper.packetevents.protocol.entity.data.EntityDataTypes;
import com.github.retrooper.packetevents.protocol.entity.type.EntityTypes;
import com.github.retrooper.packetevents.util.Vector3d;
import com.github.retrooper.packetevents.wrapper.play.server.*;
import org.bukkit.*;
import org.bukkit.command.*;
import org.bukkit.entity.Player;
import org.bukkit.event.*;
import org.bukkit.event.inventory.*;
import org.bukkit.event.player.*;
import org.bukkit.inventory.*;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.util.Vector;
import java.io.IOException;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;

public final class CosmeticPets extends JavaPlugin implements Listener {
    private static final AtomicInteger NEXT_ID = new AtomicInteger(-1000000000);
    private final Map<UUID, Pet> pets = new HashMap<>();
    private final Set<UUID> refreshing = new HashSet<>();
    private Preferences preferences;
    private int interval;

    @Override public void onEnable() {
        try { preferences = new Preferences(getDataFolder().toPath().resolve("players.yml")); }
        catch (IOException e) {
            getLogger().severe("Could not load players.yml. Correct or restore it before enabling CosmeticPets.");
            getServer().getPluginManager().disablePlugin(this); return;
        }
        getServer().getPluginManager().registerEvents(this, this);
        interval = 5;
        getServer().getScheduler().runTaskTimer(this, this::tick, 1L, interval);
    }
    @Override public void onDisable() {
        for (Pet pet : pets.values()) destroy(pet);
        pets.clear();
        for (Player player : Bukkit.getOnlinePlayers())
            if (player.getOpenInventory().getTopInventory().getHolder() instanceof Menu) player.closeInventory();
    }
    private void send(Player player, com.github.retrooper.packetevents.wrapper.PacketWrapper<?> packet) {
        if (player.isOnline()) PacketEvents.getAPI().getPlayerManager().sendPacket(player, packet);
    }
    private void destroy(Pet pet) {
        for (UUID id : pet.viewers) {
            Player viewer = Bukkit.getPlayer(id);
            if (viewer != null) send(viewer, new WrapperPlayServerDestroyEntities(pet.id));
        }
        pet.viewers.clear();
    }
    private void remove(UUID owner) {
        Pet pet = pets.remove(owner);
        if (pet != null) destroy(pet);
    }
    private Location destination(Player owner, PetKind kind) {
        Location base = owner.getLocation();
        double angle = Math.toRadians(base.getYaw());
        Location behind = base.clone().add(Math.sin(angle) * 1.6, 0, -Math.cos(angle) * 1.6);
        if (!behind.getWorld().isChunkLoaded(behind.getBlockX() >> 4, behind.getBlockZ() >> 4)) behind = base.clone();
        if (kind == PetKind.BAT) behind.add(0, 1.3, 0);
        else {
            // Use a nearby floor when possible, without loading chunks or pathfinding.
            for (int offset : new int[]{0, -1, 1, -2}) {
                Location candidate = behind.clone().add(0, offset, 0);
                if (candidate.getBlock().isPassable() && candidate.clone().add(0, 1, 0).getBlock().isPassable()
                        && candidate.clone().add(0, -1, 0).getBlock().getType().isSolid()) return candidate;
            }
        }
        if (!behind.getBlock().isPassable()) return base;
        return behind;
    }
    private void tick() {
        for (Player owner : Bukkit.getOnlinePlayers()) {
            UUID id = owner.getUniqueId();
            var choice = preferences.get(id);
            if (choice == null || !choice.summoned() || owner.isDead() || owner.getGameMode() == GameMode.SPECTATOR
                    || owner.isInvisible() || !owner.hasPermission("cosmeticpets.use")) { remove(id); continue; }
            Pet pet = pets.get(id);
            if (pet == null || pet.kind != choice.kind() || !pet.position.getWorld().equals(owner.getWorld())) {
                remove(id);
                pet = new Pet(choice.kind(), destination(owner, choice.kind()));
                pets.put(id, pet);
            }
            Location target = destination(owner, pet.kind);
            Vector delta = target.toVector().subtract(pet.position.toVector());
            double distance = delta.length();
            if (distance > 8) pet.position = target;
            else if (distance > 0.15) pet.position.add(delta.multiply(Math.min(1, 1.5 / distance)));
            pet.position.setYaw(owner.getLocation().getYaw());
            Set<UUID> visible = new HashSet<>();
            for (Player viewer : Bukkit.getOnlinePlayers()) {
                if (!viewer.getWorld().equals(owner.getWorld()) || !viewer.canSee(owner)
                        || viewer.getLocation().distanceSquared(pet.position) > 48 * 48) continue;
                visible.add(viewer.getUniqueId());
                if (pet.viewers.add(viewer.getUniqueId())) spawn(viewer, pet);
                else if (pet.last == null || pet.last.distanceSquared(pet.position) > 0.0001
                        || pet.last.getYaw() != pet.position.getYaw())
                    send(viewer, new WrapperPlayServerEntityTeleport(pet.id, vector(pet.position), pet.position.getYaw(), 0, pet.kind != PetKind.BAT));
            }
            for (UUID viewerId : new HashSet<>(pet.viewers)) if (!visible.contains(viewerId)) {
                Player viewer = Bukkit.getPlayer(viewerId);
                if (viewer != null) send(viewer, new WrapperPlayServerDestroyEntities(pet.id));
                pet.viewers.remove(viewerId);
            }
            pet.last = pet.position.clone();
        }
    }
    private Vector3d vector(Location position) { return new Vector3d(position.getX(), position.getY(), position.getZ()); }
    private void spawn(Player viewer, Pet pet) {
        var type = switch (pet.kind) { case CAT -> EntityTypes.CAT; case BAT -> EntityTypes.BAT; case ZOMBIE -> EntityTypes.ZOMBIE; };
        send(viewer, new WrapperPlayServerSpawnEntity(pet.id, Optional.of(pet.uuid), type,
                vector(pet.position), 0, pet.position.getYaw(), pet.position.getYaw(), 0, Optional.empty()));
        List<EntityData<?>> data = new ArrayList<>();
        data.add(new EntityData<>(5, EntityDataTypes.BOOLEAN, true)); // silent
        data.add(new EntityData<>(6, EntityDataTypes.BOOLEAN, true)); // no gravity
        if (pet.kind == PetKind.CAT) data.add(new EntityData<>(19, EntityDataTypes.CAT_VARIANT, 10)); // all black
        if (pet.kind == PetKind.ZOMBIE) data.add(new EntityData<>(16, EntityDataTypes.BOOLEAN, true)); // baby
        send(viewer, new WrapperPlayServerEntityMetadata(pet.id, data));
    }
    private boolean choose(Player player, PetKind kind, boolean summoned) {
        try { preferences.set(player.getUniqueId(), new Preferences.Choice(kind, summoned)); }
        catch (IOException e) { player.sendMessage(ChatColor.RED + "Could not save your pet preference. Please try again."); return false; }
        remove(player.getUniqueId());
        player.sendMessage(ChatColor.GOLD + "[Pets] " + ChatColor.GRAY + (summoned ? kind.label + " summoned." : "Pet dismissed."));
        return true;
    }
    @Override public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (!(sender instanceof Player player)) { sender.sendMessage("Use this command in-game."); return true; }
        if (!player.hasPermission("cosmeticpets.use")) return true;
        if (args.length == 0) { player.openInventory(new Menu().inventory); return true; }
        if (args.length != 1) return false;
        var choice = preferences.get(player.getUniqueId());
        switch (args[0].toLowerCase(Locale.ROOT)) {
            case "cat" -> choose(player, PetKind.CAT, true);
            case "bat" -> choose(player, PetKind.BAT, true);
            case "zombie" -> choose(player, PetKind.ZOMBIE, true);
            case "summon", "dismiss" -> {
                if (choice == null) player.sendMessage(ChatColor.YELLOW + "Choose a pet first with /pets.");
                else choose(player, choice.kind(), args[0].equalsIgnoreCase("summon"));
            }
            default -> { return false; }
        }
        return true;
    }
    @Override public List<String> onTabComplete(CommandSender sender, Command command, String alias, String[] args) {
        if (args.length != 1 || !sender.hasPermission("cosmeticpets.use")) return List.of();
        return List.of("cat", "bat", "zombie", "summon", "dismiss").stream()
                .filter(s -> s.startsWith(args[0].toLowerCase(Locale.ROOT))).toList();
    }
    private void forgetViewer(Player player) {
        for (Pet pet : pets.values()) {
            if (pet.viewers.remove(player.getUniqueId()))
                send(player, new WrapperPlayServerDestroyEntities(pet.id));
        }
    }
    @EventHandler public void quit(PlayerQuitEvent event) {
        remove(event.getPlayer().getUniqueId());
        forgetViewer(event.getPlayer());
    }
    @EventHandler public void world(PlayerChangedWorldEvent event) {
        remove(event.getPlayer().getUniqueId());
        // Client world switches discard fake entities; resend other pets as new spawns.
        forgetViewer(event.getPlayer());
    }
    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void teleport(PlayerTeleportEvent event) {
        getServer().getScheduler().runTask(this, () -> {
            if (event.isCancelled()) return;
            remove(event.getPlayer().getUniqueId());
            forgetViewer(event.getPlayer());
        });
    }
    @EventHandler public void respawn(PlayerRespawnEvent event) {
        remove(event.getPlayer().getUniqueId());
        forgetViewer(event.getPlayer());
    }
    @EventHandler(priority = EventPriority.HIGHEST) public void click(InventoryClickEvent event) {
        if (!(event.getView().getTopInventory().getHolder() instanceof Menu)) return;
        event.setCancelled(true);
        if (!(event.getWhoClicked() instanceof Player player)) return;
        refresh(player);
        if (!player.hasPermission("cosmeticpets.use")) return;
        if (event.getClick() != ClickType.LEFT && event.getClick() != ClickType.RIGHT) return;
        switch (event.getRawSlot()) {
            case 11 -> choose(player, PetKind.CAT, true);
            case 13 -> choose(player, PetKind.BAT, true);
            case 15 -> choose(player, PetKind.ZOMBIE, true);
            case 21, 23 -> {
                var choice = preferences.get(player.getUniqueId());
                if (choice != null) choose(player, choice.kind(), event.getRawSlot() == 21);
                else player.sendMessage(ChatColor.YELLOW + "Choose a pet first.");
            }
        }
    }
    @EventHandler(priority = EventPriority.HIGHEST) public void drag(InventoryDragEvent event) {
        if (event.getView().getTopInventory().getHolder() instanceof Menu) {
            event.setCancelled(true);
            if (event.getWhoClicked() instanceof Player player) refresh(player);
        }
    }
    @EventHandler public void close(InventoryCloseEvent event) {
        if (event.getInventory().getHolder() instanceof Menu && event.getPlayer() instanceof Player player) refresh(player);
    }
    private void refresh(Player player) {
        if (!isEnabled() || !refreshing.add(player.getUniqueId())) return;
        getServer().getScheduler().runTask(this, () -> {
            refreshing.remove(player.getUniqueId());
            if (player.isOnline()) player.updateInventory();
        });
    }
    private static ItemStack icon(Material material, String name, String lore) {
        ItemStack item = new ItemStack(material);
        ItemMeta meta = item.getItemMeta(); meta.setDisplayName(ChatColor.GOLD + name);
        meta.setLore(List.of(ChatColor.GRAY + lore)); item.setItemMeta(meta); return item;
    }
    private static final class Menu implements InventoryHolder {
        final Inventory inventory = Bukkit.createInventory(this, 27, "Halloween Pets");
        Menu() {
            inventory.setItem(11, icon(Material.CAT_SPAWN_EGG, "Black Cat", "Click to summon your companion."));
            inventory.setItem(13, icon(Material.BAT_SPAWN_EGG, "Bat", "Click to summon your companion."));
            inventory.setItem(15, icon(Material.ZOMBIE_SPAWN_EGG, "Baby Zombie", "Click to summon your companion."));
            inventory.setItem(21, icon(Material.LIME_DYE, "Summon", "Summon your saved pet."));
            inventory.setItem(23, icon(Material.RED_DYE, "Dismiss", "Dismiss your pet; keep your selection."));
        }
        @Override public Inventory getInventory() { return inventory; }
    }
    private static final class Pet {
        final int id = NEXT_ID.getAndDecrement();
        final UUID uuid = UUID.randomUUID();
        final PetKind kind;
        final Set<UUID> viewers = new HashSet<>();
        Location position, last;
        Pet(PetKind kind, Location position) { this.kind = kind; this.position = position; }
    }
}
