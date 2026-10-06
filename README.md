# CosmeticPets

Free Halloween companions for LARP SMP (Purpur 26.3). Requires **PacketEvents 2.14.0 or newer**. No client mods or resource packs. Built with Java 17; the server itself needs the Java version required by Purpur. Folia is not supported. Java-client visuals require in-game validation; Geyser/Bedrock visuals are not verified.

## Use

`/pets` opens the Halloween menu. Choose a **Black Cat**, **Bat**, or **Baby Zombie**. `/pets cat`, `/pets bat`, and `/pets zombie` also select and summon companions. `/pets dismiss` hides yours while remembering the selection; `/pets summon` brings it back. Everyone has `cosmeticpets.use` by default. There are no purchases or abilities.

Selection and summon state are saved by UUID in `plugins/CosmeticPets/players.yml`. Summoned pets return on reconnect/restart and follow between worlds. They temporarily disappear while dead, invisible or spectating. One pet per player. Nearby players within 48 blocks see it if they can see the owner; vanished owners' pets are hidden from viewers for whom Bukkit canSee is false.

## Cosmetic behavior

These are packet-only visual mobs, not actual server entities: no combat, collision, item drops, experience, pressure plates, breeding, mob AI reactions or item pickup. Player interaction packets cannot act on them because their IDs do not belong to server entities. They follow using visual position updates every five ticks, with a short catch-up teleport when far away. Bats float beside the owner. Ground pets use nearby floor space when possible; movement is visual rather than AI pathfinding and can clip on complex terrain. No chunks are deliberately loaded for pets. All visuals are removed when the plugin disables or the owner leaves. No world entity cleanup is needed.

## Install

Install PacketEvents, then download **CosmeticPets** from the latest successful **Actions → Build** run. Extract `CosmeticPets-1.0.0.jar` to `plugins/` and restart. If PacketEvents is already installed, use that installation rather than adding a second JAR.

## Verification

CI builds with `mvn verify` and tests saved preferences, independent owners, dismissed selection and invalid-file preservation. Test the menu against shift-click/number-key/offhand/drag attempts, verify reconnect/restart and world changes do not duplicate pets, and check the cat variant, bat appearance and baby zombie on your actual client. Test vanish and spectator transitions before enabling for staff accounts. Gameplay isolation follows from using no actual server entities; packet rendering still requires live-client verification.
