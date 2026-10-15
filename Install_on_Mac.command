#!/bin/bash
cd "$(dirname "$0")" || exit 1
printf '\nMPK249 Universal v2: Mac setup\n\n'
/usr/bin/env python3 Tools/install_mac.py
printf '\nInstall companion files and Vital mappings? (type YES to proceed) > '
IFS= read -r answer
if [ "$answer" = YES ]; then
   /usr/bin/env python3 Tools/install_mac.py --install
else
   echo 'No changes made.'
fi
printf '\nPress Return to close.\n'
IFS= read -r _