virsh-start-stop
===

I wanted to start and stop individual libvirt virtual machines with a systemd unit.

Calling "virsh start %i" or "virsh stop %i" from the unit doesn't cut it because it doesn't block while
shutting down so you don't know if it was successful without extra work.
Starting a machine is also challenging because "virsh start uses exit status 1 for multiple error conditions,
including "machine is already running".

The purpose of this script is to start / stop a given virtual machine, handling the "already running" case gracefully
and in a blocking fashion while shutting down, with the option to yank the virtual power cord from the machine in case
it ignores our polite requests.

Example systemd unit file:
```
[Unit]
Description=virsh start / stop %i
Requires=libvirtd.service
After=libvirtd.service

[Service]
Type=oneshot
RemainAfterExit=true
ExecStart=/opt/vollmerhaus.net/venv/bin/virsh-start-stop --machine %i --state started
ExecStop=/opt/vollmerhaus.net/venv/bin/virsh-start-stop --machine %i --state stopped --timeout 80

[Install]
WantedBy=default.target
```
