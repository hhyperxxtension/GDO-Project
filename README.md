## Распределенная система кэширования данных пользователей с микросервисной архитектурой.

## VPS 23.10.2025

| name            | ip addres     |
| --------------- | ------------- |
| backend-go      | 51.250.96.39  |
| frontend-python | 51.250.18.217 |

## Проверка работы

```bash
curl 51.250.18.217:5000/user?id=3
```


## Структура проекта

├── **backend**             Исходные файлы backend

├── **backend-api-deb**     Сборка backend в deb пакет

├── **frontend**            Исходные файлы frontend

└── **rpmbuild**            Сборка frontend в rpm пакет

└──**iptables.sh**          Файл настройки правил фаерволла для backend и frontend
  

## Архитектура

```

[Клиент] -> [Frontend API (Python/Flask)] -> [Redis Cache]
                        |
                        v
            [Backend API (Go)] -> [PostgreSQL]

```

## Описание проекта

Проект представляет собой распределенную систему, состоящую из трех основных компонентов:
- Backend API (Go) - сервис для работы с базой данных PostgreSQL
- Frontend API (Python) - сервис кэширования с использованием Redis
- Конфигурация системы через YAML файлы

### Компоненты системы

1. **Backend API** (Go):
   - REST API для работы с базой данных PostgreSQL
   - Конфигурируемое подключение к БД
   - Endpoint `/user` для получения информации о пользователе

2. **Frontend API** (Python/Flask):
   - Кэширующий слой с использованием Redis
   - Проксирование запросов к Backend API
   - Автоматическое кэширование ответов
   - TTL кэша: 60 секунд

## Установка

### Backend API
1. Debian-пакет:

```bash
dpkg -i backend-api-deb/backend-api.deb
```

2. Конфигурация:
   - Основной конфиг: `/etc/backend-api/config.yaml`
   - Systemd сервис: `/etc/systemd/system/backend-api.service`

  

### Frontend API

1. RPM-пакет:

```bash
   rpm -i rpmbuild/RPMS/x86_64/cache-api-1.0-1.el9.x86_64.rpm
```

2. Конфигурация:
   - Основной конфиг: `/etc/cache-api/config-api.yaml`
   - Systemd сервис: `/etc/systemd/system/cache-api.service`

  

## Переменные окружения

### Backend API
- `CONFIG_PATH` - путь к конфигурационному файлу

### Frontend API
- `CONFIG_PATH` - путь к конфигурационному файлу

## Сборка пакетов

### RPM (Frontend API)

```bash
cp -r rpmbuild ~/
cd ~/rpmbuild/SPECS
rpmbuild -ba cache-api.spec
```
### DEB (Backend API)

```bash
cd backend-api-deb
dpkg-deb --build . ../backend-api.deb
```