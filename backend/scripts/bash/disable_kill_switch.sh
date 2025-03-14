#!/bin/bash

# Скрипт отключения kill-switch на macOS (сброс правил pf)
# Используйте sudo при запуске: sudo ./disable_kill_switch.sh

PF_CONF="/etc/pf.conf"

echo "Отключаем kill-switch и восстанавливаем стандартные правила pf..."

# Отключаем pf
sudo pfctl -d

# Сбрасываем стандартную конфигурацию pf из /etc/pf.conf
sudo pfctl -Fa -f "$PF_CONF"

echo "Kill-switch отключён, сетевые настройки восстановлены."
