Name:           cache-api
Version:        1.0
Release:        1%{?dist}
Summary:        Flask API with Redis cache
License:        MIT
URL:            https://github.com/hhyperxxtension/GDO-Project
Source0:        %{name}-%{version}.tar.gz

BuildArch:      x86_64
Requires:       python3 systemd redis

%description
Simple Flask API for database with Redis cache, bundled deps.

%prep
%setup -q

%install
# Создаём директории
install -d %{buildroot}/opt/%{name}
install -d %{buildroot}/opt/%{name}/lib/python/site-packages
install -d %{buildroot}/etc/%{name}
install -d %{buildroot}/etc/systemd/system

# Копируем файлы приложения
cp cache-api.py %{buildroot}/opt/%{name}/
cp config-api.yaml %{buildroot}/etc/%{name}/

# Устанавливаем зависимости в изолированную site-packages (используем системный pip)
%{_bindir}/pip3 install --no-cache-dir --target %{buildroot}/opt/%{name}/lib/python/site-packages Flask redis requests PyYAML


# Копируем systemd-юнит и правим ExecStart на wrapper
#sed 's|/usr/bin/python3| /opt/%{name}/run.sh|' cache-api.service > %{buildroot}/etc/systemd/system/%{name}.service
cp cache-api.service %{buildroot}/etc/systemd/system/%{name}.service
chmod 644 %{buildroot}/etc/systemd/system/%{name}.service

# Создаём директорию для логов (опционально)
install -d %{buildroot}/var/log/%{name}

%pre
# Создаём пользователя перед установкой
getent group flaskapiuser >/dev/null || groupadd -r flaskapiuser
getent passwd flaskapiuser >/dev/null || useradd -r -g flaskapiuser -s /sbin/nologin -d /opt/cache-api flaskapiuser

%post
# Перезагружаем systemd после установки
systemctl daemon-reload
systemctl enable %{name}.service

%preun
if [ $1 -eq 0 ]; then  # Полное удаление
    systemctl stop %{name}.service
    systemctl disable %{name}.service
    userdel flaskapiuser
    groupdel flaskapiuser
fi

%postun
systemctl daemon-reload

%files
%defattr(-,flaskapiuser,flaskapiuser,-)
%dir %attr(755,flaskapiuser,flaskapiuser) /opt/%{name}
%dir %attr(755,root,root) /etc/%{name}
%dir %attr(755,root,root) /var/log/%{name}
%attr(744,flaskapiuser,flaskapiuser) /opt/%{name}/cache-api.py
%attr(644,flaskapiuser,flaskapiuser) /etc/%{name}/config-api.yaml
%attr(644,root,root) /etc/systemd/system/%{name}.service
/opt/%{name}/lib/python/site-packages/

%changelog
* Fri Oct 17 2025 oleg o.shev.russia@gmail.com - 1.0-1
- Initial package
