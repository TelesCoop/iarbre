#!/bin/bash
set -eux
echo CHANGE_ME > vault.key
openssl rand -base64 40 > new_vault.key
ansible-vault rekey --new-vault-password-file new_vault.key  group_vars/all/cross_env_vault.yml
mv new_vault.key vault.key
ansible-vault view group_vars/all/cross_env_vault.yml
