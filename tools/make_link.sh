#!/bin/bash
#
# Создает символическую ссылку на зависимость Node.js - Bootstrap - в папке static.
# Адрес корневого каталога проекта определяется автоматически.

project_root="$(dirname "$(dirname "$(readlink -fm "$0")")")"
cd $project_root
ln -s ../node_modules static/node_modules
