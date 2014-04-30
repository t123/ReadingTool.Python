function Get-ScriptDirectory
{
    $Invocation = (Get-Variable MyInvocation -Scope 1).Value;
    if($Invocation.PSScriptRoot)
    {
        $Invocation.PSScriptRoot;
    }
    Elseif($Invocation.MyCommand.Path)
    {
        Split-Path $Invocation.MyCommand.Path
    }
    else
    {
        $Invocation.InvocationName.Substring(0,$Invocation.InvocationName.LastIndexOf("\"));
    }
}

$currentDir = Get-ScriptDirectory
$parent = (get-Item $currentDir).Parent
$files = Get-ChildItem $currentDir -Filter *.ui

echo "`n`n`n`nFound $($files.Length) files"
$processed = 0

foreach($file in $files) {
    try {
        $outputFile = [io.path]::GetFileNameWithoutExtension($file) + ".py"
        $output =  "$($parent.Fullname)\ui\$outputFile"

        $command = "pyuic5 $($file.FullName)"
        write-host "Writing $output" -NoNewline
        iex $command | Out-File -FilePath "$output" -Encoding "utf8"
        $processed++
        write-host "`t...OK" -ForegroundColor Green
    }
    catch [system.exception]
    {
        write-host "`t...FAILED" -ForegroundColor Yellow
    }
}

if($processed -eq $files.Length) 
{    
    write-host "`n`nSUCCESS: Finished $processed files" -ForegroundColor Green
}
else 
{
    write-host "`n`WARNING: Only finished $processed/$($files.Length) files" -ForegroundColor Red
}