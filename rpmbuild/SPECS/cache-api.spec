Name:           cache-api
Version:        1.0
Release:        1%{?dist}
Summary:        Flask API with Redis cache

License:        GPLv#
URL:            https://github.com/hhyperxxtension/GDO-Project
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  noarch
Requires:       python3
Requires:       redis

%description
Flask-based API app

%prep
%autosetup


%build
%configure
%make_build


%install

VENV_DIR=%{buildroot}%{_prefix}/lib/cache-api/venv
mkdir -p $VENV_DIR


# Создаём virtual environment
python3 -m venv $VENV_DIR

# Активируем venv и устанавливаем зависимости (используем --no-deps, чтобы избежать подзависимостей)
$VENV_DIR/bin/pip install --no-deps --upgrade pip
$VENV_DIR/bin/pip install Flask redis requests PyYAML

# Устанавливаем основной скрипт в venv/bin для удобства (с shebang на venv python)
install -D -m 755 cache-api.py $VENV_DIR/bin/cache-api.py
# Делаем скрипт исполняемым и добавляем shebang для venv
sed -i '1i#!/usr/lib/cache-api/venv/bin/python' $VENV_DIR/bin/cache-api.py
chmod +x $VENV_DIR/bin/cache-api.py

# Устанавливаем конфиг
install -D -m 644 config-api.yaml %{buildroot}%{_sysconfdir}/cache-api/config-api.yaml

# Устанавливаем systemd-юнит (обновлённый, см. ниже)
install -D -m 644 cache-api.service %{buildroot}%{_unitdir}/cache-api.service

# Создаём симлинк для удобства запуска ( /opt/cache-api/cache-api -> venv/bin/cache-api)
mkdir -p %{buildroot}%{_opt}/cache-api
ln -s /usr/lib/cache-api/venv/bin/cache-api.py %{buildroot}%{_opt}/cache-api/cache-api.py

%post
# После установки: перезагрузка systemd и включение сервиса
systemctl daemon-reload
systemctl enable cache-api.service
# Опционально: старт сервиса
# systemctl start cache-api.service

%postun
# После удаления: отключение и остановка сервиса
if [ $1 -eq 0 ]; then
    systemctl disable cache-api.service || true
    systemctl stop cache-api.service || true
fi
systemctl daemon-reload

%files
# Включаем весь venv (это основной размер пакета)
%{_prefix}/lib/cache-api/venv/

# Симлинк в /usr/bin
%{_bindir}/cache-api

# Конфиг (не перезаписывать при обновлении)
%config(noreplace) %{_sysconfdir}/cache-api/config-api.yaml

# Systemd-юнит
%{_unitdir}/cache-api.service

%changelog
* Thu Oct 16 2025 oleg
- 
