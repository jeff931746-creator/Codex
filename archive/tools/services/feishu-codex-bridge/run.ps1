param([ValidateSet('bridge', 'named-tunnel', 'quick-tunnel')][string]$Mode = 'bridge')
$ErrorActionPreference = 'Stop'
$node = if ($env:NODE_BIN) { $env:NODE_BIN } else { (Get-Command node -ErrorAction Stop).Source }
& $node (Join-Path $PSScriptRoot 'run.mjs') $Mode
exit $LASTEXITCODE
