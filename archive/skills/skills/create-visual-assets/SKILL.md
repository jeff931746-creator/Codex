---
name: create-visual-assets
description: Create or edit visual assets by routing vector-native work to direct SVG authoring and raster or AI-generated imagery to the company Pango MCP with the fixed GPT-image-2 model. Use when Codex is asked to make SVG artwork, icons, diagrams not covered by Mermaid, PNG/JPG/WebP images, illustrations, concept art, mockups, image variants, or edits based on reference images, especially when the workspace requires Pango rather than a generic image generator.
---

# Create Visual Assets

Route each request by output type, create the asset with the required tool path, and verify the delivered result.

## Route the request

1. Confirm the requested visual, intended use, output format, dimensions or aspect ratio, and target path when those details materially affect the result.
2. Choose exactly one primary route:
   - Write SVG directly when the result is vector-native and can be expressed with SVG/XML, CSS, gradients, filters, masks, paths, shapes, and text.
   - Use Pango `generate_image` when the result is a raster image, illustration, concept image, texture, mockup, or reference-image edit.
3. Use both routes only for a genuinely mixed deliverable. Keep the generated raster asset separate unless the user asks to embed it in the SVG.
4. Route Mermaid source rendering to `mmd-to-image`; do not duplicate that workflow here.

## Create SVG directly

1. Author the SVG as text. Do not call a raster image-generation model for a pure SVG request.
2. Include a valid root `svg`, explicit `viewBox`, and dimensions or responsive sizing appropriate to the requested use.
3. Keep reusable definitions in `defs`. Prefer vector paths and shapes over embedded raster data.
4. Avoid external fonts, scripts, remote images, and environment-specific dependencies unless the user explicitly requires them.
5. Validate the XML structure. Render or preview the SVG when visual layout matters, then fix clipping, unreadable text, incorrect stacking, and broken references.

## Generate raster images with Pango

1. Use the configured `pango-skillsrv` MCP server.
2. Call `generate_image` with `model` fixed to `gpt-image-2`.
3. Always provide a concrete `prompt`. Preserve the user's subject, style, composition, camera, lighting, palette, text, and exclusion constraints; do not replace them with generic art direction.
4. Set `n`, `size`, `quality`, and `include_cos_urls` from the request. When unspecified, use the service defaults and avoid inventing requirements that affect cost or composition.
5. For image editing or variants, pass the source images through `reference_images`. Use no more than 8 images and keep each image at or below 10 MB.
6. Use the `model` slug, not the display name. Do not silently substitute another Pango model or a generic image generator.
7. If `gpt-image-2` is unavailable, the MCP server is missing, or authentication fails, stop and report the exact blocker. Ask to repair or reload the Pango connection before generating.

## Verify and deliver

1. Confirm the output exists and is non-empty when a file was requested.
2. Inspect the result when visual quality matters. Check composition, legibility, requested content, aspect ratio, unwanted artifacts, and consistency with reference images.
3. Iterate through the same route. Do not switch models or output types merely because the first attempt needs refinement.
4. Return the preview and the saved file path or COS URL that the user requested.
5. Never print, save, or copy the Pango token into the project, skill, prompt, logs, or generated artifacts.

## Invocation examples

- `Use $create-visual-assets to create a scalable SVG icon set for these four states.`
- `Use $create-visual-assets to generate a 1536x1024 concept image with Pango GPT-image-2.`
- `Use $create-visual-assets to edit this reference image while preserving the character and composition.`
