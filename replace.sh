#!/bin/bash

echo "$1"
grep -Hrnl "$1"|xargs -i sed -i "s/$1/$2/g" {}
