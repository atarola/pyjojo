## Changelog

### Version 0.9

- Escape all environment variables passed to the scripts. [#36]

### Version 0.8

- Added /script_names route [#29]
- Split output on newlines in stderr and stdout [#18]
- Added tags to scripts [#18, #30]
- Added combined output of stdout and stderr [#26]

### Version 0.7

- Fix for versions of python < 2.7, ssl does not support cipher option. [#16]

### Version 0.6

- Unix Domain Socket Support [#9]
- Switched the parsing of htpasswd files to use passlib [#10]
- Explicitly set SSL ciphers to HIGH,MEDIUM [#13]
