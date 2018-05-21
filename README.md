# Station reporting

## Installation

To install the station reporting as a *systemd* service, simple run
`make install`. Service will be run in current directory, so do not remove
repository!

To uninstall a service, run `make uninstall`.

*Note*: `make install` and `make uninstall` require access to *systemd* files
(will usually require superuser to run this command).
