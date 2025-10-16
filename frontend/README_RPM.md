# Building an RPM for the `frontend` folder

This guide explains how to create an RPM package from the files in this `frontend/` folder.

What we added
- `frontend.spec` - RPM spec file that packages files into /opt/gdo/frontend and installs a systemd unit at /etc/systemd/system/cache-api.service if present.
- `pack-rpm.sh` - helper script to create the source tarball and optionally run `rpmbuild`.

Basic approach
1. Create a source tarball named `gdo-frontend-1.0.0.tar.gz` containing the contents of this folder.
2. Place the tarball in `~/rpmbuild/SOURCES` and the spec file in `~/rpmbuild/SPECS`.
3. Run `rpmbuild -ba frontend.spec` on a Linux host to produce RPMs.

Options for Windows users

Using WSL (recommended)
1. Open WSL (Ubuntu or other distro) and mount the Windows path, e.g. your repo might be at `/mnt/d/GDO/GDO-Project/frontend`.
2. cd to that path and run:

```bash
chmod +x pack-rpm.sh
./pack-rpm.sh --build
```

This will create the tarball and run `rpmbuild`. Ensure `rpm-build` is installed in WSL: `sudo apt install rpm` or on Fedora `sudo dnf install rpm-build`.

Using Docker (no host install of rpmbuild)
```powershell
# run from PowerShell in repo root (Windows)
docker run --rm -v ${PWD}:/src -w /src/frontend centos:7 /bin/bash -c "yum install -y rpm-build tar && chmod +x pack-rpm.sh && ./pack-rpm.sh --build"
```

Using a remote Linux host
1. scp the folder or tarball to the remote host.
2. Run the same `rpmbuild` steps there.

Manual steps (what `pack-rpm.sh` does)
1. Create tarball: `gdo-frontend-1.0.0.tar.gz` containing folder contents.
2. mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
3. mv gdo-frontend-1.0.0.tar.gz ~/rpmbuild/SOURCES/
4. cp frontend.spec ~/rpmbuild/SPECS/
5. rpmbuild -ba ~/rpmbuild/SPECS/frontend.spec

After build
- Binary RPM will be in `~/rpmbuild/RPMS/noarch/`.
- Source RPM will be in `~/rpmbuild/SRPMS/`.

Assumptions and notes
- Package is built as noarch and installs files under `/opt/gdo/frontend`.
- The spec installs `cache-api.service.ini` as `/etc/systemd/system/cache-api.service` and reloads systemd during postinstall.
- Adjust `License`, `URL`, `Version` in `frontend.spec` as needed.

Edge cases
- If you need files under different ownership or with specific permissions, update the `%install` section in `frontend.spec`.
- If `cache-api.service.ini` is actually a systemd unit file, consider renaming to `cache-api.service` and ensuring `Type` and `ExecStart` lines are correct.

If you'd like, I can:
- Update the spec to include proper %doc, changelog, or dependency fields.
- Build the RPM inside a container and return the generated RPM file.
