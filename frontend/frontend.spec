Name:           gdo-frontend
Version:        1.0.0
Release:        1%{?dist}
Summary:        GDO frontend cache API files

License:        MIT
URL:            https://example.local/gdo
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRoot:      %{_tmppath}/%{name}-%{version}-build

%description
Lightweight package containing the frontend cache API scripts and configs for GDO.

%prep
%setup -q

%build
# no build step

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/opt/gdo/frontend
cp -a * %{buildroot}/opt/gdo/frontend/

# install systemd unit if present
if [ -f cache-api.service.ini ]; then
    mkdir -p %{buildroot}/etc/systemd/system
    install -m 0644 cache-api.service.ini %{buildroot}/etc/systemd/system/cache-api.service
fi

%files
%defattr(-,root,root,-)
/opt/gdo/frontend
/etc/systemd/system/cache-api.service

%post
if [ -f /etc/systemd/system/cache-api.service ]; then
    systemctl daemon-reload || true
fi

%preun
if [ $1 -eq 0 ]; then
    # package is being removed
    if [ -f /etc/systemd/system/cache-api.service ]; then
        systemctl stop cache-api.service >/dev/null 2>&1 || true
        systemctl disable cache-api.service >/dev/null 2>&1 || true
    fi
fi

%postun
if [ -f /etc/systemd/system/cache-api.service ]; then
    systemctl daemon-reload || true
fi

%changelog
* Fri Oct 16 2025 Packager <packager@example.local> - 1.0.0-1
- Initial package
