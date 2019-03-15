#!/bin/bash
set -e

FILENAME="group_vars/all/vault/password.yaml"

if [ "$1" == "--clear" ]; then
    ENCRYPT="no"
else
    ENCRYPT="yes"
fi

read -p "Enter the admin username [default: admin]: " USER
if [ "x$USER" == "x" ]; then
    USER="admin"
fi
read -s -p "Enter password for $USER: " PASSWORD
echo ""
read -s -p "Renter password for $USER: " PASSWORD2
echo ""

if [ "$PASSWORD2" != "$PASSWORD" ]; then
    echo "Passwords do not match" >&2
    exit 1
fi
if [ "x$PASSWORD" == "x" ]; then
    echo "No password given" >&2
    exit 1
fi

mkdir -p `dirname $FILENAME`
echo "---" > $FILENAME
echo "admin_principal: $USER" >> $FILENAME
echo "admin_password: $PASSWORD" >> $FILENAME
echo ""

if [ "$ENCRYPT" == "yes" ]; then
    ansible-vault encrypt --ask-vault-pass $FILENAME
fi
