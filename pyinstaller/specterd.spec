# -*- mode: python ; coding: utf-8 -*-
import platform
import subprocess
import mnemonic, os
from embit import util as embit_util

mnemonic_path = os.path.join(mnemonic.__path__[0], "wordlist")
embit_libsecp_binary = embit_util.ctypes_secp256k1._find_library()

block_cipher = None

binaries = []
if platform.system() == 'Windows':
    binaries = [("./windll/libusb-1.0.dll", ".")]
    packaged_software_datas = [
        ('./torbrowser/tor-win64-0.4.5.7.zip', 'torbrowser'),
        ('./bitcoind/bitcoin-0.21.1-win64.zip', 'bitcoind'),
    ]
elif platform.system() == 'Linux':
    if platform.processor() == 'aarch64': #ARM 64 bit
        binaries = [("/lib/aarch64-linux-gnu/libusb-1.0.so.0", ".")]
    else:
        candidates = [
                "/usr/lib/libusb-1.0.so.0",
                "/lib/x86_64-linux-gnu/libusb-1.0.so.0",
                "/lib/aarch64-linux-gnu/libusb-1.0.so.0",
                "/lib/arm-linux-gnueabihf/libusb-1.0.so.0",
        ]
        binaries = []
        for p in candidates:
            if os.path.isfile(p):
                binaries = [(p, ".")]
                break
    packaged_software_datas = [
        ('./torbrowser/tor-browser-linux64-10.0.15_en-US.tar.xz', 'torbrowser'),
        ('./bitcoind/bitcoin-0.21.1' + ('-arm-linux-gnueabihf.tar.gz' if "armv" in platform.machine() else '-x86_64-linux-gnu.tar.gz'), 'bitcoind')
    ]
elif platform.system() == 'Darwin':
    find_brew_libusb_proc = subprocess.Popen(['brew', '--prefix', 'libusb'], stdout=subprocess.PIPE)
    libusb_path = find_brew_libusb_proc.communicate()[0]
    binaries = [(libusb_path.rstrip().decode() + "/lib/libusb-1.0.dylib", ".")]
    packaged_software_datas = [
        ('./torbrowser/TorBrowser-10.0.15-osx64_en-US.dmg', 'torbrowser'),
        ('./bitcoind/bitcoin-0.21.1-osx64.tar.gz', 'bitcoind'),
    ]

a = Analysis(['specterd.py'],
             binaries=binaries,
             datas=[('../src/cryptoadvance/specter/templates', 'templates'), 
                    ('../src/cryptoadvance/specter/services/templates', 'templates'),
                    ('../src/cryptoadvance/specter/static', 'static'),
                    ('../src/cryptoadvance/specter/translations','translations'),
                    (mnemonic_path, 'mnemonic/wordlist'),
                    (embit_libsecp_binary, 'embit/util/prebuilt'),
                    ("version.txt", "."),
                    *packaged_software_datas,
             ],
             hiddenimports=[
                'pkg_resources.py2_warn',
                'cryptoadvance.specter.config'
             ],
             hookspath=['hooks/'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

if platform.system() == 'Linux':
    import hwilib
    a.datas += Tree('../udev', prefix='hwilib/udev')

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
name=os.getenv("specterd_filename","specterd")
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name=name,
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
