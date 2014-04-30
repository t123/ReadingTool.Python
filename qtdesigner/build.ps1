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

echo "Found $($files.Length) files"
$processed = 0

foreach($file in $files) {
    try {
        $outputFile = [io.path]::GetFileNameWithoutExtension($file) + ".py"
        $output =  "$($parent.Fullname)\ui\$outputFile"

        $command = "pyuic5 $($file.FullName)"
        echo "Writing $output"
        iex $command | Out-File -FilePath "$output" -Encoding "utf8"
        $processed++
    }
    catch [system.exception]
    {
        echo "WARNING: Could not process file $outputFile"
    }
}

if($processed -eq $files.Length) 
{    
    echo "`n`nSUCCESS: Finished $processed files"
}
else 
{
    echo "`n`WARNING: Only finished $processed/$($files.Length) files"
}