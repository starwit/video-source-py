# Build & Development of video source package

## Docker

You can use [docker_build.sh](docker_build.sh) to build an image for local testing.

Once build you can run Docker image locally like so:
```bash
docker run -it --rm -v ./settings.yaml:/code/ starwitorg/sae-video-source-py:1.1.0
```
Please note, that you should provide a settings.yaml that configures application to your needs. See [template](settings.template.yaml) for how to do that.

## APT package

This software can be released as a Debian/APT package. This section explains, how this works. Please note, that everything has been tested with Ubuntu Linux only.

Following packages need to installed on your computer:
* build-essential
* python3-all
* python3-setuptools 
* python3-pip
* dh-python

Package can be build using:
```bash
make build-deb
```

If you don't want to install all pre-requisites to your machine, you can use APT build container:
```
docker run -it --rm -v ./:/code  starwitorg/debian-packaging:0.0.2 bash -l -c "export PATH=~/.local/bin/:$PATH; cd /code; make"
```

Package can be found in folder _target_. You can test install package using Docker like so:
```bash
docker run -it --rm -v ./:/app  ubuntu:22.04 bash
# Run in container
apt update && apt install -y /app/target/video-source-py_0.1.0_all.deb
```

Please note, that SystemD won't run in Docker (makes no sense), so this test install will fail all systemctl steps.

```bash
make clean
```

### Config files for packaging

Files in the `debian/` folder:
- `changelog` - Records changes made to the package in each version
- `compat` - Specifies the debhelper compatibility level
- `control` - Contains package metadata (dependencies, description, etc.)
- `install` - Lists files to be installed and their destination paths
- `objectdetector.service` - Systemd service file for the application
- `postinst` - Post-installation script that runs after package installation
- `preinst` - Pre-installation script that runs before package installation
- `prerm` - Pre-removal script that runs before package removal
- `rules` - Main package build script (makefile)
- `source/options` - Options for the source package format like ommiting directories