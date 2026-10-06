package io.github.aemiroo.cosmeticpets;

import com.github.retrooper.packetevents.PacketEvents;
import com.github.retrooper.packetevents.protocol.entity.type.EntityTypes;
import com.github.retrooper.packetevents.util.Vector3d;
import com.github.retrooper.packetevents.wrapper.play.server.*;
import org.bukkit.*;
import org.bukkit.command.*;
import org.bukkit.entity.Player;
import org.bukkit.entity.ItemDisplay;
import org.bukkit.entity.Display;
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
    private final Set<UUID> ghostPackLoaded = new HashSet<>();
    private static final UUID GHOST_PACK_ID = UUID.fromString("81e3f811-1da1-4454-b12b-c452ff67ef16");
    private byte[] ghostPackHash;
    private long animationTick;

    @Override public void onEnable() {
        saveDefaultConfig();
        if (!getConfig().getBoolean("pet-packets-enabled", false)) {
            getLogger().warning("CosmeticPets is in emergency safe mode; no pet packets will be sent.");
            getServer().getPluginManager().disablePlugin(this);
            return;
        }
        try { preferences = new Preferences(getDataFolder().toPath().resolve("players.yml")); }
        catch (IOException e) {
            getLogger().severe("Could not load players.yml. Correct or restore it before enabling CosmeticPets.");
            getServer().getPluginManager().disablePlugin(this); return;
        }
        getServer().getPluginManager().registerEvents(this, this);
        try (var input = getResource("ghost-pack.sha1")) {
            if (input == null) throw new IOException("Missing ghost-pack.sha1");
            ghostPackHash = HexFormat.of().parseHex(new String(input.readAllBytes(), java.nio.charset.StandardCharsets.UTF_8).trim());
        } catch (IOException | IllegalArgumentException e) {
            getLogger().severe("Ghost pack hash unavailable; ghost visuals will remain hidden.");
        }
        for (Player player : Bukkit.getOnlinePlayers()) requestGhostPack(player);
        interval = 1;
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
        if (pet.kind == PetKind.GHOST) {
            if (pet.display != null) { pet.display.remove(); pet.display = null; }
            pet.viewers.clear();
            pet.displayLast = null;
            pet.scareTicks = 0;
            return;
        }
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
    private Location destination(Player owner, PetKind kind, float followYaw) {
        Location base = GhostMotion.upright(owner.getLocation());
        double angle = Math.toRadians(followYaw);
        Location behind = base.clone().add(Math.sin(angle) * 1.6, 0, -Math.cos(angle) * 1.6);
        if (!behind.getWorld().isChunkLoaded(behind.getBlockX() >> 4, behind.getBlockZ() >> 4)) behind = base.clone();
        if (kind == PetKind.BAT || kind == PetKind.GHOST) behind.add(0, 1.3 + (kind == PetKind.GHOST ? GhostMotion.bob(animationTick) : 0), 0);
        else {
            // Use a nearby floor when possible, without loading chunks or pathfinding.
            for (int offset : new int[]{0, -1, 1, -2}) {
                Location candidate = behind.clone().add(0, offset, 0);
                if (clear(candidate, kind)
                        && candidate.clone().add(0, -1, 0).getBlock().getType().isSolid()) return candidate;
            }
        }
        if (clear(behind, kind)) return behind;
        if (clear(base, kind)) return base;
        return null;
    }
    private Collision.Point point(Location at) { return new Collision.Point(at.getX(), at.getY(), at.getZ()); }
    private boolean clear(Location at, PetKind kind) {
        double halfWidth = kind == PetKind.GHOST ? 0.5 : 0.35;
        if (kind == PetKind.GHOST) at = at.clone().add(0, -0.5, 0);
        double height = switch (kind) { case CAT -> 0.75; case BAT -> 0.95; case GHOST -> 1.0; case ZOMBIE -> 1.95; };
        World world = at.getWorld();
        int minX = (int) Math.floor(at.getX() - halfWidth), maxX = (int) Math.floor(at.getX() + halfWidth);
        int minZ = (int) Math.floor(at.getZ() - halfWidth), maxZ = (int) Math.floor(at.getZ() + halfWidth);
        int minY = (int) Math.floor(at.getY() + 0.001), maxY = (int) Math.floor(at.getY() + height);
        if (minY < world.getMinHeight() || maxY >= world.getMaxHeight()) return false;
        for (int x = minX; x <= maxX; x++) for (int z = minZ; z <= maxZ; z++) {
            if (!world.isChunkLoaded(x >> 4, z >> 4)) return false;
            for (int y = minY; y <= maxY; y++)
                if (!world.getBlockAt(x, y, z).isPassable()) return false;
        }
        return true;
    }
    private void tick() {
        animationTick++;
        for (Player owner : Bukkit.getOnlinePlayers()) {
            UUID id = owner.getUniqueId();
            var choice = preferences.get(id);
            if (choice != null && choice.kind() != PetKind.GHOST && animationTick % 2 != 0) continue;
            if (choice == null || !choice.summoned() || owner.isDead() || owner.getGameMode() == GameMode.SPECTATOR
                    || owner.isInvisible() || !owner.hasPermission("cosmeticpets.use")) { remove(id); continue; }
            Pet pet = pets.get(id);
            if (pet == null || pet.kind != choice.kind() || !pet.position.getWorld().equals(owner.getWorld())) {
                remove(id);
                Location initial = destination(owner, choice.kind(), owner.getLocation().getYaw());
                if (initial == null) continue;
                pet = new Pet(choice.kind(), initial);
                pet.ownerLast = owner.getLocation();
                pet.followYaw = owner.getLocation().getYaw();
                pets.put(id, pet);
            }
            Location ownerPosition = owner.getLocation();
            Vector ownerDelta = ownerPosition.toVector().subtract(pet.ownerLast.toVector());
            if (ownerDelta.getX() * ownerDelta.getX() + ownerDelta.getZ() * ownerDelta.getZ() > 0.0025)
                pet.followYaw = Motion.turn(pet.followYaw, Motion.heading(ownerDelta.getX(), ownerDelta.getZ()), pet.kind == PetKind.GHOST ? 12 : 24);
            pet.ownerLast = ownerPosition;
            Location target = destination(owner, pet.kind, pet.followYaw);
            if (target == null) { remove(id); continue; }
            Vector delta = target.toVector().subtract(pet.position.toVector());
            double distance = delta.length();
            boolean ghost = pet.kind == PetKind.GHOST;
            float turnLimit = ghost ? 12 : 24;
            boolean catchUp = distance > 12 || pet.blockedTicks >= (ghost ? 40 : 20);
            if (catchUp) { destroy(pet); pet.position = target; pet.last = null; pet.blockedTicks = 0; }
            else if (distance > (ghost ? 0.002 : 0.06)) {
                double step = ghost ? GhostMotion.step(distance) : Motion.step(distance);
                Location before = pet.position.clone();
                Vector desired = delta.clone().multiply(step / distance);
                Collision.Point from = point(before);
                Collision.Point end = from.add(desired.getX(), desired.getY(), desired.getZ());
                Pet active = pet;
                Collision.Point reached = Collision.slide(from, end,
                        at -> clear(new Location(before.getWorld(), at.x(), at.y(), at.z()), active.kind));
                pet.position.setX(reached.x()); pet.position.setY(reached.y()); pet.position.setZ(reached.z());
                if (Collision.distance(reached, end) > 0.0025) pet.blockedTicks++;
                else pet.blockedTicks = 0;
                if (delta.getX() * delta.getX() + delta.getZ() * delta.getZ() > 0.0001)
                    pet.position.setYaw(Motion.turn(pet.position.getYaw(),
                            Motion.heading(delta.getX(), delta.getZ()), turnLimit));
            }
            else pet.blockedTicks = 0;
            // Match legacy relative-packet precision to prevent accumulated drift.
            if (!ghost) {
                pet.position.setX(Motion.quantize(pet.position.getX()));
                pet.position.setY(Motion.quantize(pet.position.getY()));
                pet.position.setZ(Motion.quantize(pet.position.getZ()));
            }
            if (pet.kind == PetKind.GHOST) { updateGhost(owner, pet); pet.last = pet.position.clone(); continue; }
            Set<UUID> visible = new HashSet<>();
            for (Player viewer : Bukkit.getOnlinePlayers()) {
                if (!viewer.getWorld().equals(owner.getWorld()) || !viewer.canSee(owner)
                        || viewer.getLocation().distanceSquared(pet.position) > 48 * 48) continue;
                visible.add(viewer.getUniqueId());
                if (pet.viewers.add(viewer.getUniqueId())) spawn(viewer, pet);
                else if (pet.last == null || pet.last.distanceSquared(pet.position) > 0
                        || pet.last.getYaw() != pet.position.getYaw())
                    move(viewer, pet, catchUp);
            }
            for (UUID viewerId : new HashSet<>(pet.viewers)) if (!visible.contains(viewerId)) {
                Player viewer = Bukkit.getPlayer(viewerId);
                if (viewer != null) send(viewer, new WrapperPlayServerDestroyEntities(pet.id));
                pet.viewers.remove(viewerId);
            }
            pet.last = pet.position.clone();
        }
    }
    private void move(Player viewer, Pet pet, boolean catchUp) {
        if (catchUp || pet.last == null) {
            send(viewer, new WrapperPlayServerEntityTeleport(pet.id, vector(pet.position),
                    pet.position.getYaw(), 0, pet.kind != PetKind.BAT));
        } else {
            send(viewer, new WrapperPlayServerEntityRelativeMoveAndRotation(pet.id,
                    pet.position.getX() - pet.last.getX(), pet.position.getY() - pet.last.getY(),
                    pet.position.getZ() - pet.last.getZ(), pet.position.getYaw(), 0, pet.kind != PetKind.BAT));
        }
    }
    private Vector3d vector(Location position) { return new Vector3d(position.getX(), position.getY(), position.getZ()); }
    private void spawn(Player viewer, Pet pet) {
        var type = switch (pet.kind) { case CAT -> EntityTypes.CAT; case BAT -> EntityTypes.BAT; case ZOMBIE -> EntityTypes.ZOMBIE; case GHOST -> throw new IllegalStateException("Ghosts use native displays"); };
        send(viewer, new WrapperPlayServerSpawnEntity(pet.id, Optional.of(pet.uuid), type,
                vector(pet.position), 0, pet.position.getYaw(), pet.position.getYaw(), 0, Optional.empty()));
        // Use client defaults: metadata indices vary by protocol version.
        // Never send hardcoded fields (26.3 field 6 is Pose, not a boolean).
    }
    private void requestGhostPack(Player player) {
        String url = getConfig().getString("ghost.resource-pack-url",
                "https://github.com/aemiroo/CosmeticPets/releases/download/ghost-pack/CosmeticPets-Ghost-Pack.zip");
        if (ghostPackHash == null || url == null || url.isBlank()) return;
        player.addResourcePack(GHOST_PACK_ID, url, ghostPackHash,
                "Optional pack for the cosmetic ghost companion", false);
    }
    @EventHandler public void join(PlayerJoinEvent event) {
        getServer().getScheduler().runTaskLater(this, () -> {
            if (event.getPlayer().isOnline()) requestGhostPack(event.getPlayer());
        }, 40L);
    }
    @EventHandler public void packStatus(PlayerResourcePackStatusEvent event) {
        if (!GHOST_PACK_ID.equals(event.getID())) return;
        if (event.getStatus() == PlayerResourcePackStatusEvent.Status.SUCCESSFULLY_LOADED)
            ghostPackLoaded.add(event.getPlayer().getUniqueId());
        else if (event.getStatus() != PlayerResourcePackStatusEvent.Status.ACCEPTED
                && event.getStatus() != PlayerResourcePackStatusEvent.Status.DOWNLOADED) {
            ghostPackLoaded.remove(event.getPlayer().getUniqueId());
            forgetViewer(event.getPlayer());
        }
    }
    private void updateGhost(Player owner, Pet pet) {
        pet.position.setPitch(0);
        boolean hasViewer = Bukkit.getOnlinePlayers().stream().anyMatch(viewer ->
                ghostPackLoaded.contains(viewer.getUniqueId()) && viewer.getWorld().equals(owner.getWorld())
                && viewer.canSee(owner) && viewer.getLocation().distanceSquared(pet.position) <= 48 * 48);
        if (!hasViewer) { destroy(pet); return; }
        if (pet.display == null || !pet.display.isValid()) {
            pet.viewers.clear();
            if (pet.display != null) pet.display.remove();
            ItemStack model = new ItemStack(Material.PAPER);
            ItemMeta meta = model.getItemMeta();
            meta.setItemModel(new NamespacedKey("cosmeticpets", "ghost"));
            model.setItemMeta(meta);
            pet.display = pet.position.getWorld().spawn(pet.position, ItemDisplay.class, display -> {
                display.setVisibleByDefault(false);
                display.setPersistent(false);
                display.setGravity(false);
                display.setInvulnerable(true);
                display.setSilent(true);
                display.setItemStack(model);
                display.setItemDisplayTransform(ItemDisplay.ItemDisplayTransform.FIXED);
                display.setBillboard(Display.Billboard.FIXED);
                display.setBrightness(new Display.Brightness(15, 15));
                display.setTeleportDuration(1);
                display.setViewRange(0.75f);
                display.setDisplayWidth(0.9f);
                display.setDisplayHeight(0.95f);
            });
        }
        if (animationTick % 20 == 0 && pet.scareTicks == 0
                && ghostPackLoaded.contains(owner.getUniqueId())
                && owner.getLocation().distanceSquared(pet.position) <= 16
                && RareScare.roll(java.util.concurrent.ThreadLocalRandom.current()::nextInt)) {
            pet.scareTicks = RareScare.DURATION;
            owner.sendMessage(ChatColor.LIGHT_PURPLE + "[Pets] Boo! " + ChatColor.WHITE + "♥");
            owner.playSound(pet.position, Sound.ENTITY_ALLAY_AMBIENT_WITHOUT_ITEM, 0.35f, 1.8f);
            owner.spawnParticle(Particle.HEART, pet.position.clone().add(0, 0.5, 0), 3, 0.2, 0.1, 0.2, 0);
        }
        Location displayed = pet.position.clone();
        if (pet.scareTicks > 0) {
            Location hop = displayed.clone().add(0, RareScare.hop(pet.scareTicks), 0);
            if (clear(hop, PetKind.GHOST)) displayed = hop;
            pet.scareTicks--;
        }
        if (pet.displayLast == null || pet.displayLast.distanceSquared(displayed) > 0
                || pet.displayLast.getYaw() != displayed.getYaw()) pet.display.teleport(displayed);
        pet.displayLast = displayed;

        Set<UUID> visible = new HashSet<>();
        for (Player viewer : Bukkit.getOnlinePlayers()) {
            if (!ghostPackLoaded.contains(viewer.getUniqueId()) || !viewer.getWorld().equals(owner.getWorld())
                    || !viewer.canSee(owner) || viewer.getLocation().distanceSquared(pet.position) > 48 * 48) continue;
            visible.add(viewer.getUniqueId());
            if (pet.viewers.add(viewer.getUniqueId())) viewer.showEntity(this, pet.display);
        }
        for (UUID viewerId : new HashSet<>(pet.viewers)) if (!visible.contains(viewerId)) {
            Player viewer = Bukkit.getPlayer(viewerId);
            if (viewer != null) viewer.hideEntity(this, pet.display);
            pet.viewers.remove(viewerId);
        }
    }
    private boolean choose(Player player, PetKind kind, boolean summoned) {
        try { preferences.set(player.getUniqueId(), new Preferences.Choice(kind, summoned)); }
        catch (IOException e) { player.sendMessage(ChatColor.RED + "Could not save your pet preference. Please try again."); return false; }
        remove(player.getUniqueId());
        if (kind == PetKind.GHOST && summoned && !ghostPackLoaded.contains(player.getUniqueId()))
            player.sendMessage(ChatColor.YELLOW + "Accept the optional ghost resource pack to see your ghost.");
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
            case "ghost" -> choose(player, PetKind.GHOST, true);
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
        return List.of("cat", "bat", "zombie", "ghost", "summon", "dismiss").stream()
                .filter(s -> s.startsWith(args[0].toLowerCase(Locale.ROOT))).toList();
    }
    private void forgetViewer(Player player) {
        for (Pet pet : pets.values()) {
            if (pet.viewers.remove(player.getUniqueId())) {
                if (pet.display != null) player.hideEntity(this, pet.display);
                else if (pet.kind != PetKind.GHOST) send(player, new WrapperPlayServerDestroyEntities(pet.id));
            }
        }
    }
    @EventHandler public void quit(PlayerQuitEvent event) {
        ghostPackLoaded.remove(event.getPlayer().getUniqueId());
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
            case 17 -> choose(player, PetKind.GHOST, true);
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
            inventory.setItem(11, icon(Material.CAT_SPAWN_EGG, "Cat", "Click to summon your companion."));
            inventory.setItem(13, icon(Material.BAT_SPAWN_EGG, "Bat", "Click to summon your companion."));
            inventory.setItem(15, icon(Material.ZOMBIE_SPAWN_EGG, "Zombie", "Click to summon your companion."));
            inventory.setItem(17, icon(Material.GHAST_TEAR, "Ghost", "Requires the optional ghost resource pack."));
            inventory.setItem(21, icon(Material.LIME_DYE, "Summon", "Summon your saved pet."));
            inventory.setItem(23, icon(Material.RED_DYE, "Dismiss", "Dismiss your pet; keep your selection."));
        }
        @Override public Inventory getInventory() { return inventory; }
    }
    private static final class Pet {
        final int id = NEXT_ID.getAndDecrement();
        final UUID uuid = UUID.randomUUID();
        final PetKind kind;
        ItemDisplay display;
        Location displayLast;
        int scareTicks;
        final Set<UUID> viewers = new HashSet<>();
        Location position, last, ownerLast;
        float followYaw;
        int blockedTicks;
        Pet(PetKind kind, Location position) { this.kind = kind; this.position = position; }
    }
}
