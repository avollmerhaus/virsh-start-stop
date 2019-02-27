#!/bin/env python3

import libvirt
import time
import argparse


def _libvirt_silence_error(*args):
    # prevent libvirt from printing on the terminal without our consent
    # https://stackoverflow.com/questions/45541725/avoiding-console-prints-by-libvirt-qemu-python-apis
    pass


def _get_libvirt_machine(machine):
    libvirt.registerErrorHandler(f=_libvirt_silence_error, ctx=None)
    conn = libvirt.open("qemu:///system")
    libvirt_machine = conn.lookupByName(machine)
    return libvirt_machine


def start_machine(machine):
    libvirt_machine = _get_libvirt_machine(machine)
    if not libvirt_machine.state()[0] == libvirt.VIR_DOMAIN_RUNNING:
        # there is a potential race condition here as well should some other process start the machine in between
        # let's see if that is really a problem in production before wrapping in try / except
        libvirt_machine.create()
        print('{}: started'.format(machine))
    else:
        print('{}: libvirt reported state VIR_DOMAIN_RUNNING, assuming it\'s true'.format(machine))


def stop_machine(machine, timeout):
    libvirt_machine = _get_libvirt_machine(machine)
    elapsed_seconds = 0

    while not libvirt_machine.state()[0] == libvirt.VIR_DOMAIN_SHUTOFF:
        # issuing ACPI shutdown a few times can sometimes convince windows guests
        # to take the request seriously instead of displaying "really shutdown?"
        # on the virtual machines console.
        try:
            libvirt_machine.shutdownFlags(libvirt.VIR_DOMAIN_SHUTDOWN_GUEST_AGENT | libvirt.VIR_DOMAIN_SHUTDOWN_ACPI_POWER_BTN)
        except libvirt.libvirtError as err:
            # we have a race condition between checking for VIR_DOMAIN_SHUTOFF
            # and issuing the shutdown request.
            # unfortunately, "libvirtError" is all we get in that case.
            if libvirt_machine.state()[0] == libvirt.VIR_DOMAIN_SHUTOFF:
                # if the domain is in SHUTOFF now, we assume all went well
                pass
            else:
                # if not, re-raise
                raise
        time.sleep(1)
        elapsed_seconds += 1
        if elapsed_seconds == timeout:
            # graceful as in "send sigterm to qemu-kvm", this is still akin to yanking the virtual power cord
            libvirt_machine.destroyFlags(libvirt.VIR_DOMAIN_DESTROY_GRACEFUL)
            print('{}: had to yank the virtual powercord'.format(machine))
    print('{}: shutdown took {} seconds'.format(machine, elapsed_seconds))


def cli_interface():
    parser = argparse.ArgumentParser(description='start / stop libvirt VMs in a blocking fashion')
    parser.add_argument('--machine', metavar='myVM', type=str, required=True, help='machine name')
    parser.add_argument('--state', metavar='[started | stopped]', type=str, required=True, help = 'desired machine state')
    parser.add_argument('--timeout', metavar='80', type=int, required=False, default=0, help='timeout sec for graceful shutdown request, yank virtual powercord afterwards. ignored when 0 (the default).')
    args = parser.parse_args()

    if args.state == 'stopped':
        stop_machine(args.machine, args.timeout)

    if args.state == 'started':
        start_machine(args.machine)


if __name__ == '__main__':
    cli_interface()
