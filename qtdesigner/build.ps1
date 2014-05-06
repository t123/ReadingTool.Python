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

write-host "`nFound $($files.Count) files`n" -BackgroundColor Red -ForegroundColor White
$processed = 0

foreach($file in $files) {
    try {
        $outputFile = [io.path]::GetFileNameWithoutExtension($file) + ".py"
        $output =  "$($parent.Fullname)\ui\views\$outputFile"

        $command = "pyuic4 $($file.FullName)"
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

if($processed -eq $files.Count) 
{    
    write-host "`nSUCCESS: Finished $processed files" -ForegroundColor Green
}
else 
{
    write-host "`nWARNING: Only finished $processed/$($files.Length) files" -ForegroundColor Red
}