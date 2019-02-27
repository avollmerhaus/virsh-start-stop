virsh-start-stop
===

I wanted to start and stop individual libvirt virtual machines with a systemd unit.

Calling `virsh start %i` or `virsh stop %i` from the unit doesn't cut it.
This is because it doesn't block while shutting down so you don't know if the machine is really down unless you wrap 
it all in a bash script and employ a dirty hack along the lines of `virsh list | grep myVM`.

Starting a machine is also challenging because `virsh start` uses exit status 1 for multiple error conditions,
including "machine is already running".

The purpose of this script is to start / stop a given virtual machine through the libvirt python bindings in a way that
is easily consumable from systemd. 
This means I try to handle the "already running" case gracefully.
Shutting down happens in a blocking fashion, with the option to yank the virtual power cord from the machine in case
it ignores our polite requests.

I also took the opportunity to issue shutdown requests every second until the machine is down.
This should be unnecessary when the virtual machine has the libvirt guest agent running, but it can sometimes help
to convince windows to really shut down instead of asking "really shutdown?" on the virtual console with nobody around
to click ok.   

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
