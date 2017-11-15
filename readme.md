# iTunes Backup Filename Unobfuscater

## Background

iOS does not allow direct access of files in specific app. The only way to do is to do full backup via iTunes, and find out the files you needed from the backup. Unfortunately, the filenames in the backup are obfuscated. Fortunately, the real human-readable filenames are stored in a sqlite database. This little script can rename the files inplace to human-readable filenames according to the database. It also supports reverting back to original obfuscated filenames.

## Requirement

* Python 2.7 or above
* Tested on Windows, but should work in OSX
* Backup via iTunes with NO password

## Usage

### Under Windows

To rename
```
python ibfu.py "%USERPROFILE%\AppData\Roaming\Apple Computer\MobileSync\Backup\XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```
*Please replace XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX with the real folder name found on your computer

To undo
```
python ibfu.py -u "%USERPROFILE%\AppData\Roaming\Apple Computer\MobileSync\Backup\XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

For additional features, see help
```
python ibfu.py -h
``` 

## Licence
AGPL v3.0