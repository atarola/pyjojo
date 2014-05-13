## Changelog

### Version 0.6

- Unix Domain Socket Support [#9]
- Switched the parsing of htpasswd files to use passlib [#10]
- Explicitly set SSL ciphers to HIGH,MEDIUM [#13]

### Version 0.7

- fix for versions of python < 2.7, ssl does not support cipher option [#16]
