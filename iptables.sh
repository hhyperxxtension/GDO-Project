#!/bin/bash

# Проверяем аргументы
if [ $# -ne 1 ]; then
    echo "Использование: $0 <vm1|vm2>"
    exit 1
fi

VM_TYPE=$1
BACKEND_IP="51.250.96.39"  # IP VM1 (Backend/PG)
PROXY_IP="51.250.18.217"    # IP VM2 (Proxy/Redis)

# Функция для очистки правил (опционально)
flush_rules() {
    iptables -F
    iptables -X
    iptables -t nat -F
    iptables -t nat -X
    iptables -t mangle -F
    iptables -t mangle -X
    iptables -P INPUT ACCEPT
    iptables -P FORWARD ACCEPT
    iptables -P OUTPUT ACCEPT
}

# Установка политики по умолчанию
set_default_policy() {
    iptables -P INPUT DROP
    iptables -P FORWARD DROP
    iptables -P OUTPUT ACCEPT  # Выходящий трафик разрешаем (для инициации соединений)
}

# Разрешение локального трафика
allow_loopback() {
    iptables -A INPUT -i lo -j ACCEPT
}

# Разрешение SSH (из ADMIN_IP)
allow_ssh() {
    iptables -A INPUT -p tcp --dport 22 -j ACCEPT
}

case $VM_TYPE in
    "vm1")
        echo "Настройка фаерволла для VM1 (Ubuntu: Backend + PostgreSQL)"
        
        # Очистка (раскомментируй при необходимости)
        # flush_rules
        
        set_default_policy
        allow_loopback
        allow_ssh
        
        # Backend принимает запросы ТОЛЬКО от Proxy (VM2 IP) на порт 8080
        iptables -A INPUT -p tcp --dport 8080 -s $PROXY_IP -j ACCEPT
        
        # Backend имеет доступ только к PostgreSQL (локально, на той же VM)
        # (Для OUTPUT это уже разрешено политикой; INPUT от localhost)
        iptables -A INPUT -p tcp --sport 5432 -i lo -j ACCEPT
        
        # PostgreSQL принимает подключения ТОЛЬКО от Backend (локально)
        iptables -A INPUT -p tcp --dport 5432 -s 127.0.0.1 -j ACCEPT
        
        echo "Правила для VM1 применены. Сохрани: iptables-save > /etc/iptables.rules"
        ;;
    
    "vm2")
        echo "Настройка фаерволла для VM2 (CentOS: Proxy + Redis)"
        
        # Очистка (раскомментируй при необходимости)
        # flush_rules
        
        set_default_policy
        allow_loopback
        allow_ssh
        
        # Proxy принимает запросы от ЛЮБОГО источника на порт 5000
        iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
        
        # Proxy имеет доступ к Redis (локально, на той же VM)
        iptables -A INPUT -p tcp --sport 6379 -i lo -j ACCEPT
        
        # Proxy имеет доступ к Backend
        sudo iptables -A INPUT -p tcp --sport 8080 -s $BACKEND_IP -j ACCEPT
        

        # Redis: не принимает внешние подключения (только локально от Proxy)
        iptables -A INPUT -p tcp --dport 6379 -s 127.0.0.1 -j ACCEPT
        
        echo "Правила для VM2 применены. Сохрани: iptables-save > /etc/iptables.rules"
        ;;
    
    *)
        echo "Ошибка: укажи vm1 или vm2"
        exit 1
        ;;
esac

# Вывод текущих правил
echo "=== Текущие правила INPUT ==="
iptables -L INPUT -v -n