import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="virsh_start_stop",
    version="0.0.1",
    author="Aljoscha Vollmerhaus",
    author_email='pydev@aljoscha.vollmerhaus.net',
    description="Utilize the python libvirt API to start and stop qemu-kvm machines in a blocking fashion",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/avollmerhaus/virsh_start_stop",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console"
    ],
    install_requires=['libvirt-python'],
    packages=setuptools.find_packages('src'),
    package_dir={'':'src'},
    entry_points={
        'console_scripts': ['virsh-start-stop = virsh_start_stop.virsh_start_stop:cli_interface', ],
    },
)