param(
    [ValidateSet('bridge', 'named-tunnel', 'quick-tunnel')][string]$Mode = 'bridge',
    [switch]$Remove
)
$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'Windows Task Scheduler is required.' }
$taskName = "FeishuCodex-$Mode"
if ($Remove) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    exit 0
}
$node = if ($env:NODE_BIN) { (Get-Item $env:NODE_BIN).FullName } else { (Get-Command node -ErrorAction Stop).Source }
$script = Join-Path $PSScriptRoot 'run.mjs'
$action = New-ScheduledTaskAction -Execute $node -Argument ('"{0}" {1}' -f $script, $Mode) -WorkingDirectory $PSScriptRoot
$user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $user
$principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Write-Output "Registered $taskName for next logon. Start-ScheduledTask -TaskName '$taskName' starts it now."
