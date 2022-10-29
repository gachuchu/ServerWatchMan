# @charset "utf-8"

do {
	$storage_info = Get-Volume
}while($null -eq $storage_info)

$storage_info |
  Where-Object {($_.DriveType -eq "Fixed") -And ($_.DriveLetter -ne $null)} |
  Sort-Object -Property DriveLetter |
  Select-Object DriveLetter,Size,SizeRemaining |
  Export-Csv $Args[0] -Encoding utf8 -NoTypeInformation
