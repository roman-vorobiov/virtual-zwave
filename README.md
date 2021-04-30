Requirements
===

Python 3.9: build from [sources](https://github.com/python/cpython/tree/3.9)

    python3 -m pip install -r requirements.txt

How to run
===

Run tests:

    python3 -m pytest

Mock Z-Wave USB stick by creating a pseudo-tty device at the desired location:

    python3 virtual_controller.py --link=/tmp/ttyV1

Simulate the network and serve web client on `localhost:3000`:

    python3 virtual_network.py

How to contribute
===

Todo...

Useful documentation
===

[Guideline for developing serial API based host applications](https://www.silabs.com/documents/login/user-guides/INS12350-Serial-API-Host-Appl.-Prg.-Guide.pdf)

[Z-Wave 500 Series Appl. Programmers Guide v6.81.0x](https://www.silabs.com/documents/public/user-guides/INS13954-Instruction-Z-Wave-500-Series-Appl-Programmers-Guide-v6_81_0x.pdf)

[Z-Wave Plus Device Type Specification](https://www.silabs.com/documents/login/miscellaneous/SDS11847-Z-Wave-Plus-Device-Type-Specification.pdf)

[Z-Wave Device Class Specification](https://www.silabs.com/documents/public/miscellaneous/SDS10242-Z-Wave-Device-Class-Specification.pdf)

[Z-Wave Application Security Layer (S0)](https://www.silabs.com/documents/public/reference-manuals/SDS10865-Z-Wave-Application-Security-Layer-S0.pdf)
