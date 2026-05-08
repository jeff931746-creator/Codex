---
name: forevernine-material-downloader
description: Use when the user wants to search, resolve, and download materials from ForeverNine's public-opinion material library at public-opinion.forevernine.net, especially when the site requires reusing an existing Chrome login session and downloading files by exact material title.
---

# ForeverNine Material Downloader

Use this skill when the task is to fetch materials from `https://public-opinion.forevernine.net/domestic-material-lib/index` or related ForeverNine material-library pages.

## What This Skill Covers

- Reusing an already logged-in Chrome session
- Enabling AppleScript JavaScript control in Chrome when needed
- Querying the real material API from the logged-in browser context
- Resolving exact material titles to downloadable static file URLs
- Downloading matched files into a local folder

## Preconditions

- The user is already logged in to the ForeverNine material site in Chrome, or can log in interactively.
- Chrome is installed.
- If AppleScript JS control fails, ask the user to enable:
  `View -> Developer -> Allow JavaScript from Apple Events`

## Fast Path

1. Confirm Chrome has a tab open for the material library.
2. Use AppleScript against Chrome to reuse the logged-in session.
3. Query the material API from the page context, not from plain `curl`, because direct requests may return `未登录`.
4. Resolve exact material titles through the API.
5. Download the returned static asset URLs with `curl -L`.

## Known Working API Pattern

Call from the logged-in page context:

- Endpoint: `/api/material/client/get-material-v2`
- Method: `POST`
- Required JSON fields:
  - `source`: `inland` for the domestic library
  - `type`: `2d` or `3d`
  - `title`: exact material title when searching by name
  - `page`
  - `pageSize`

Known-good request body:

```json
{
  "page": 1,
  "pageSize": 3,
  "source": "inland",
  "type": "2d",
  "title": "素材完整标题"
}
```

## Response Notes

Successful matches are in:

```json
data.data[]
```

Useful fields:

- `title`
- `filename`
- `url[0]`
- `cover`
- `format`
- `width`
- `height`
- `size`

Static files are typically hosted on:

- `https://base-gz-static.forevernine.com/...`

## Chrome Automation Notes

Useful AppleScript pattern to locate the tab:

```applescript
tell application "Google Chrome"
  repeat with w in every window
    repeat with t in every tab of w
      if URL of t contains "public-opinion.forevernine.net/domestic-material-lib/index" then
        return t
      end if
    end repeat
  end repeat
end tell
```

Useful JavaScript pattern to run inside the tab:

```js
window.__codexResult = 'PENDING';
var xhr = new XMLHttpRequest();
xhr.open('POST', '/api/material/client/get-material-v2', true);
xhr.setRequestHeader('Content-Type', 'application/json');
xhr.onreadystatechange = function () {
  if (xhr.readyState === 4) {
    window.__codexResult = xhr.responseText;
  }
};
xhr.send(JSON.stringify({
  page: 1,
  pageSize: 3,
  source: 'inland',
  type: '2d',
  title: '素材完整标题'
}));
```

Then read back `window.__codexResult` in a second AppleScript call after a short wait.

## Download Convention

- Default output folder:
  `/Users/mt/Documents/Codex/forevernine_downloads`
- Keep the original material title as the filename when possible.
- Verify the files with `ls -lh` after download.

## Failure Modes

- `{"code":401,"msg":"未登录"}`:
  The request was made outside the logged-in browser session.
- `参数【source】不能为空`:
  Add `source: "inland"`.
- `参数【source】必须在【inland,outland,outland_2d】列表里面`:
  Use one of the accepted source values.
- `参数【type】不能为空`:
  Add `type`.
- `参数【type】必须在【2d,3d】列表里面`:
  Use `2d` or `3d`.
- AppleScript returns `missing value`:
  Store results in `window.__codex...` first, then read them back in a second call.

## Recommended Workflow

For each requested title:

1. Query `type: "2d"` first.
2. If no match, query `type: "3d"`.
3. Use the exact returned `url[0]` as the download URL.
4. Download with `curl -L -o <target-file>`.
5. Confirm all files landed in the target folder.
