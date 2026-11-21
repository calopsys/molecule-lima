# End-to-end test

This directory contains a Molecule scenario that tests the driver on a real Lima VM.

The scenario does these steps:

1. It creates the VM `molecule-lima-e2e` (2 CPUs, 2 GiB of memory, 10 GiB of disk).
2. It writes a file in the VM.
3. It reads the file and checks its content.
4. It deletes the VM.

## Requirements

- An `x86_64` Linux machine with `limactl` and `qemu-system-x86_64`.
- Python 3.13 or later.
- A user that is not root. `limactl` does not run as root.
- Internet access for the VM image.
- No VM with the name `molecule-lima-e2e`. The scenario deletes a VM with this name.

## Run

Run these commands from the root of the repository:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
cd e2e
molecule test
```

The test passes when `molecule test` gives exit status 0 and the `SCENARIO RECAP` line shows `failed=0`.

## Without KVM

If `/dev/kvm` is not available, Lima uses software emulation. The first start of the VM then takes 20 to 30 minutes. The driver stops the start after 600 seconds, so `molecule test` fails at the `create` stage.

For this case, increase the two timeouts of the driver temporarily. Run these commands in the `e2e` directory:

```bash
sed -i -e 's/async: 600/async: 3000/' \
  -e 's/limactl start --name=/limactl start --timeout=45m --name=/' \
  ../src/molecule_lima/playbooks/tasks/create_instance.yml
molecule test
git restore ../src/molecule_lima/playbooks/tasks/create_instance.yml
```

Do not commit the change to `create_instance.yml`.
