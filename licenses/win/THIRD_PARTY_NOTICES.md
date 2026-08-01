# Third-party components

This online bootstrap test downloads but does not redistribute the archives in the original ZIP.

| Component | Version/commit | Source | License handling |
|---|---|---|---|
| xPack Windows Build Tools | 4.4.1-3 | xPack release | Retain licenses in extracted distro-info |
| xPack GNU RISC-V Embedded GCC | 14.2.0-3 | xPack release | Retain licenses in extracted distro-info |
| Python | 3.14.6 | python.org | Retain Python license from archive |
| hidapi | 0.15.0 | PyPI wheel | Retain wheel dist-info licenses |
| ch32fun | 1e4887e... | cnlohr/ch32fun | Retain MIT LICENSE in test subset |

The final participant release requires a complete SBOM, corresponding-source review, and license audit.


## rv003usb

- Upstream: cnlohr/rv003usb
- Commit: `75d926abe89a3002020b989015eab97ce5ad0470`
- License: MIT
- test19 setup downloads the three core source files and LICENSE from commit-pinned Raw URLs.
