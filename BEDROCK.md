# Bedrock companions through Geyser

This port supplies original ghost and pumpkin geometry, RGBA textures, attachables,
Geyser v2 item mappings, and display mappings. It targets **local Geyser-Spigot**
with optional floodgate. Geyser does not automatically convert Java resource packs.

## Install

1. Install a current Geyser build supporting v2 mappings (API 2.9.3 / build 1062 or newer).
2. Install a **GeyserDisplayEntity build compatible with your Geyser and Java protocol**
   from [the extension project](https://github.com/GeyserExtensionists/GeyserDisplayEntity).
   Put its JAR in `plugins/Geyser-Spigot/extensions/`. It is a Geyser extension,
   not a Bukkit plugin. Install its supplied `GeyserDisplayEntityPack.mcpack`
   in `plugins/Geyser-Spigot/packs/` as well. The extension and its pack are separate
   third-party downloads and are not bundled or modified by CosmeticPets.
3. Download these files from [our pack release](https://github.com/aemiroo/CosmeticPets/releases/tag/ghost-pack):

   | File | Destination |
   | --- | --- |
   | `CosmeticPets-Bedrock.mcpack` | `plugins/Geyser-Spigot/packs/` |
   | `cosmeticpets-geyser-mappings.json` | `plugins/Geyser-Spigot/custom_mappings/` |
   | `cosmeticpets-display-mappings.yml` | `plugins/Geyser-Spigot/extensions/geyserdisplayentity/Mappings/` |

   Create destination folders if missing. Keep other plugins' mapping files.
4. In Geyser's existing `config.yml`, set these keys under its existing `gameplay` section:

   ```yaml
   gameplay:
     enable-custom-content: true
     force-resource-packs: true
   ```

   Requiring the packs ensures that a Bedrock player who reaches the Java server has
   downloaded the pack. This changes Geyser's pack policy for **all** its packs.
5. Install CosmeticPets 1.2.1 and add this section to `plugins/CosmeticPets/config.yml`:

   ```yaml
   bedrock:
     enabled: true
   ```

   Keep your existing `pet-packets-enabled: true` setting.
6. Restart the server and reconnect Bedrock clients. Run `/pets pumpkin` or `/pets ghost`.
   CosmeticPets detects Bedrock logins through floodgate or Geyser's API, skips the Java
   pack prompt, and permits model visibility when the config switch and display extension
   are enabled. Preferences and visibility rules remain shared with Java players.

## Validation and limits

The automated checks verify model faces, atlas coordinates, transparency, identifiers,
mapping references, and the Java build. **This is an experimental Bedrock port: it has
not been rendered or connection-tested on a live Bedrock client.** Check both pets on
your server before treating it as production-ready. The external display extension
uses Geyser internals, so matching its build to your server protocol matters.

The plugin remains responsible for following, collision checks and pumpkin hops;
the bridge translates the displays. Interpolation and squash appearance can differ
from Java. Ghost alpha is retained using Bedrock's alpha-blend material; Java's maximum
brightness override is not translated by the inspected display extension, so the ghost
may look darker on Bedrock. The rare harmless scare still uses server effects.

If companions are invisible, check Geyser's extension-load and mapping logs, confirm
both packs are offered, and ensure the extension does not hide `minecraft:paper` custom
displays. If models are offset or distorted, keep `bedrock.enabled: false` until the
bridge/version issue is resolved. Java players can continue using the Java pack.

Proxy-hosted Geyser is not supported by the local extension-presence check in this version.

## Rebuild

```sh
python3 resource-pack/build_pack.py
python3 resource-pack/build_bedrock.py
python3 -m unittest discover -s resource-pack -p 'test_*.py'
mvn verify
```

Sources: [Geyser item mappings](https://geysermc.org/wiki/geyser/custom-items/),
[Geyser packs](https://geysermc.org/wiki/geyser/packs/),
[Geyser extensions](https://geysermc.org/wiki/geyser/extensions/),
and [Microsoft geometry documentation](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/visualreference/geometry.v1.16.0?view=minecraft-bedrock-stable).
