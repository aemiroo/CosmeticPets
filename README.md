# Bouncing pumpkin (1.2.0)

Use /pets pumpkin or the Pumpkin GUI button. The original orange model has a round lobed body, darker ribs, a green calyx and a bent brown stem. It hops in a 36-tick cycle with a grounded pause, stretches slightly in flight and squashes on landing. Its base stays upright, and the animation checks body clearance. It uses a native nonpersistent invulnerable ItemDisplay: no mob AI, attacks, damage, drops, player collision or gameplay abilities. Existing follow speed, wall sliding and saved preferences apply. The ghost retains its brightness and ultra-rare Boo behavior.

Install CosmeticPets-1.2.0.jar, remove the old JAR, restart and reconnect to accept the updated optional pack. The existing ghost pack URL/config key is retained; that ZIP now contains both companions. Declining hides both custom models for that viewer. Live rendering and terrain testing remain necessary.

# Bright ghost and ultra-rare Boo (1.2.0)

Ghost displays use maximum brightness (block/sky 15), so the ghost itself appears bright at night. This is a rendering override, not real light emitted onto surrounding blocks.

Once every 20 server ticks (one second at 20 TPS), each summoned ghost rolls one uniformly random integer in [0, 100000000). Exactly zero triggers the Easter egg, for a 1-in-100-million chance per eligible roll. The owner must have loaded the ghost pack and be within four blocks; invisible/dead/spectating owners do not qualify. No extra rolls occur while a scare animation is active. More eligible ghosts mean more total server-wide rolls.

The harmless scare sends only the owner a cute Boo message, a quiet allay chirp and heart particles. Nearby pack users see a short upward hop, provided the ghost has body clearance overhead. It does not damage, knock back, teleport, apply effects or change inventory. There is no force-trigger command or boosted default chance. Tests verify the exact RNG bound and winning outcome, and hop bounds/return to base.

# Upright and smoother ghost (1.2.0)

Ghost positions now strip player look pitch, so looking up/down cannot tilt the native display. The ghost updates every server tick with one-tick client interpolation, continuous small bobbing steps, no legacy relative-packet position quantization and a per-tick speed/turn limit. Other pets retain their two-tick cadence; stuck recovery remains approximately two seconds. Tests cover pitch isolation, bob continuity and small-step movement. Low server TPS or client FPS can still affect animation.

# Translucent ghost and perimeter fringe (1.2.0)

The ghost body and underside now use partial alpha (110/255), while its face stays more visible. The former three full-depth bottom bars are replaced by a ragged fringe around all four edges, leaving a recessed central underside. Body geometry is united before emitting exterior faces so internal shared surfaces do not show through the translucent shell. All four texture sprites remain registered in the item atlas. CI checks alpha values, perimeter placement and removal of interior faces. Actual transparency appearance depends on client rendering and needs in-game verification.

Install CosmeticPets-1.2.0.jar, restart and reconnect to load the updated pack hash. If using a custom pack host, replace its ZIP too.

# Ghost texture repair (1.2.0)

The original ghost geometry loaded but its PNG textures were absent from the item atlas. The pack now explicitly registers its three sprites in assets/minecraft/atlases/items.json. CI checks every ghost texture against this atlas. The ZIP and embedded SHA-1 are rebuilt, so clients download the repaired pack after installing 1.2.0 and reconnecting. If you use a custom pack host, replace the hosted ZIP with the repaired one as well.

# CosmeticPets 1.2.0

Free cosmetic companions for LARP SMP, Purpur 26.3: cat, bat, zombie and an original floating ghost. Requires Java 21+ and PacketEvents 2.14.0+. Build uses Spigot 1.21.4 APIs; ghost resource pack targets Java Minecraft 26.3. Folia and Bedrock ghost rendering are not supported.

## Install and use

Download the CosmeticPets artifact from the successful Actions build, extract only CosmeticPets-1.2.0.jar into plugins, remove the older JAR, and restart. Keep pet-packets-enabled: true in plugins/CosmeticPets/config.yml to enable visuals. Saved UUID choices in players.yml remain compatible.

Use /pets or /pets ghost (also cat, bat, zombie, summon and dismiss). Preferences save across reconnect/restart. Everyone has cosmeticpets.use by default. The Ghost button is a ghast tear.

## Original ghost pack

The original model has a white body, scalloped tail, small arms, dark eyes/mouth and pink cheeks; no Sketchfab model/assets were copied. The build publishes CosmeticPets-Ghost-Pack.zip at:

https://github.com/aemiroo/CosmeticPets/releases/download/ghost-pack/CosmeticPets-Ghost-Pack.zip

The plugin requests this optional pack on join. Accept it to see ghosts. Declining or failed loading never kicks a player; ghosts are hidden for that viewer while the other pets keep working. Requests and status checks use a dedicated pack UUID, so another plugin's pack acceptance cannot enable ghost visuals. The pack SHA-1 is generated during build and included in the JAR. To use another host, add ghost.resource-pack-url to existing config.yml with the direct ZIP URL serving the exact supplied ZIP. Defaults also work with an existing config that lacks this key. Avoid duplicate prompts from separately assigning this same pack in server.properties.

The pack is also bundled in the Actions artifact. Java resource packs do not provide a Bedrock model; Geyser users need a separate conversion which is not included.

## Movement and isolation

All pets use the faster two-tick follow movement, swept body clearance and wall sliding. If stuck for about two seconds, they reappear at a checked clear position. Slabs/stairs are treated conservatively; this is not full pathfinding.

Cats, bats and zombies remain fake packet entities with no metadata overrides. The ghost uses one native Bukkit ItemDisplay so the server supplies version-correct metadata; it has no mob AI, gravity, combat, item drops or player collision. It is invulnerable, nonpersistent and removed on dismissal, quit, world changes and plugin shutdown. Only eligible nearby viewers who loaded the pack see it. Ghosts bob gently while floating. A server crash can leave a display alive until its chunk unloads; nonpersistent displays are not saved to world data.

## Verification

CI checks original pack model/texture references and bounds, builds the reproducible ZIP, and runs Java tests for movement, collision and persistence. Live client testing is required for pack prompt/accept/decline, ghost appearance, bobbing, visibility, reconnect, terrain and world transitions. No raw ghost entity metadata indices are used.

## Bedrock / Geyser

Version 1.2.5 also builds an experimental Bedrock pack for the ghost and pumpkin, plus both mapping files. See [BEDROCK.md](BEDROCK.md) for required GeyserDisplayEntity installation and setup. Build checks pass; live Bedrock rendering still needs testing.

### Carved pumpkin light

The pumpkin has actual three-voxel-deep eye, nose and mouth recesses. Warm emissive
back walls sit inside the cuts; the rind remains normally lit and rounded.
Java uses model-element light emission, and Bedrock separates emissive geometry
into its own material. The light is cosmetic and does not alter world lighting.

### Christmas companions (1.3.0)

Use `/pets snowman` or `/pets reindeer`, or select them in `/pets`. The snowman
wears a red scarf and top hat; the reindeer has antlers and a red nose. Both are
cosmetic only and use the shared collision-aware follow motion. Retired selections migrate to snowman in 1.3.1. Replace the Java/Bedrock packs and both
Geyser mapping files with the new build; restart and reconnect. Bedrock still
requires the separately installed GeyserDisplayEntity extension and its pack.
Bedrock rendering remains experimental until verified with a real client.

### Christmas-only lineup (1.3.1)

Only snowman and reindeer are available in commands, autocomplete, and the menu.
Cat, bat, zombie, ghost, and pumpkin have been retired. Saved retired selections
load as snowman, preserving the summoned/dismissed state. Both resource packs
now contain only Christmas models; update packs and both Geyser mapping files.
The Java pack filename and release tag remain unchanged for existing config URLs.

### Walking and snowman proportions (1.3.2)

Reindeer now walk with twelve baked leg poses, advancing with actual horizontal
travel and returning to a standing pose when stopped. They no longer bounce
while idle. The snowman's top hat is smaller and its twig arms hang down.
Update both packs and both Geyser mapping files: walking uses additional item
model definitions. These poses work without client mods; Bedrock still needs
the external display extension, and live rendering should be verified.

## 1.6.0 — Capybara and Legacy collection

Adds a free cosmetic-only Capybara (`/pets capybara`) with a four-leg walking cycle. Halloween Cat, Bat, Zombie, Ghost and Pumpkin return under Legacy • Halloween in `/pets`, with direct commands available. Legacy is a collection label; these companions remain free. Baby Yeti keeps its existing saved boss unlock and preview permission. Locked Baby Yeti slots show a black question mark with unlock instructions; the new pack supplies the question-mark icon. Update both Java and Bedrock packs and Geyser mappings for the new models.

### 1.6.1 — reference-style Capybara

Rebuilds Capybara with a boxy body, long blunt snout, small tilted ears, dark feet and pixel-patterned brown textures. A rare relaxed blink runs for 1.2 seconds after at least 3 seconds standing still, with a random 2–5 minute cooldown. Moving cancels the blink immediately and resumes its four-leg gait. Both packs include all six idle poses.

### 1.6.2 — closer Capybara proportions

Raises the back to just below head height, wraps dark muzzle color around the snout tip, moves both eyes toward the ears and darkens the legs. Retains the rare idle blink and four-leg gait.

The Capybara gait now uses 24 small sinusoidal shoulder/hip rotations, paired diagonally like a quadruped. Animation advances with distance travelled and pauses when stationary, replacing the previous three-angle snapping. Modern model rotation support: https://www.minecraft.net/en-us/article/minecraft-snapshot-25w46a

### 1.6.3 — Capybara size

Capybara now renders 35% larger by default. `capybara.scale` in config.yml accepts 0.5–2.0; restart after changing it. Existing configs use 1.35 when the setting is absent. Collision clearance and display bounds scale with the model. Requires only the new plugin JAR when the 1.6.2 pack is installed.

### 1.6.4 — multi-view Capybara reference

Adds white eye highlights, a slightly lowered snout, longer brown/dark legs, a small raised tail and larger mottled fur patches from the supplied front, rear, side and top references. Keeps the 1.35 default scale, 24-frame quadruped walk and rare blink. Update both resource packs.
