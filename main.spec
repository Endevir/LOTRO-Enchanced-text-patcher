# -*- mode: python -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['C:\\Documents\\LOTRO\\Top-gui-python-app'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries + [('datexport.dll', 'datexport.dll', 'BINARY'), ('zlib1T.dll', 'zlib1T.dll', 'BINARY'), ('msvcp71.dll', 'msvcp71.dll', 'BINARY'), ('msvcr71.dll', 'msvcr71.dll', 'BINARY'), ('msvcp90.dll', 'msvcp90.dll', 'BINARY') ],
          a.zipfiles,
          a.datas + [('bg.jpg', 'bg.jpg', 'Data')],
          name='Enchanced',
          debug=False,
          strip=False,
          upx=True,
          console=False,
		  icon='icon.ico')
