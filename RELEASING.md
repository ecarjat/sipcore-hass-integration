# Releasing SIP Core through HACS

HACS extracts a `zip_release` archive **into**
`/config/custom_components/sip_core`. Therefore the release archive must have
the SIP Core component files at its root:

```text
__init__.py
manifest.json
resources.py
www/sip_core.js
translations/en.json
```

Do **not** archive `custom_components/sip_core` itself. An archive with that
path creates the invalid nested directory
`/config/custom_components/sip_core/custom_components/sip_core` and leaves the
integration unavailable after the HACS update.

## Checklist

1. Update the version in `custom_components/sip_core/manifest.json`.
2. Build the frontend with `npm run build`.
3. From `custom_components/sip_core`, create the release archive:

   ```sh
   zip -rq /tmp/sip_core.zip . -x '__pycache__/*' '*.pyc'
   ```

4. Verify `unzip -l /tmp/sip_core.zip` lists `manifest.json` at the archive
   root — not `custom_components/sip_core/manifest.json`.
5. Upload that archive as the `sip_core.zip` asset of the GitHub release.
   The filename is significant: `hacs.json` requests exactly `sip_core.zip`.
   A label is not a filename, so do not upload a versioned filename such as
   `sip_core-v5.1.7.zip` and label it `sip_core.zip`.

   ```sh
   gh release upload "v$VERSION" /tmp/sip_core.zip
   ```

6. Verify the exact public URL before announcing the release:

   ```sh
   curl -fsSI -L "https://github.com/ecarjat/sipcore-hass-integration/releases/download/v$VERSION/sip_core.zip"
   ```
