# build.py
import os
import subprocess
import sys
from kivy.tools.packaging.pyinstaller_hooks import get_deps_all, hookspath, runtime_hooks

def build_exe():
    """بناء التطبيق كملف تنفيذي"""
    try:
        # إنشاء spec file ل PyInstaller
        spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-
from kivy_deps import sdl2, glew

block_cipher = None

a = Analysis(['main.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports={get_deps_all()},
             hookspath={hookspath()},
             runtime_hooks={runtime_hooks()},
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='ForexCryptoAnalyzer',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon='icon.ico')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
               strip=False,
               upx=True,
               upx_exclude=[],
               name='ForexCryptoAnalyzer')
        """
        
        with open('ForexCryptoAnalyzer.spec', 'w') as f:
            f.write(spec_content)
        
        # التنفيذ
        subprocess.call(['pyinstaller', 'ForexCryptoAnalyzer.spec'])
        print("تم بناء EXE بنجاح!")
        
    except Exception as e:
        print(f"خطأ في البناء: {e}")

def build_apk():
    """بناء التطبيق ك APK للأندرويد"""
    try:
        # إنشاء ملف buildozer.spec إذا لم يكن موجوداً
        if not os.path.exists('buildozer.spec'):
            subprocess.call(['buildozer', 'init'])
        
        # التعديل على الإعدادات إذا لزم الأمر
        subprocess.call(['buildozer', 'android', 'debug', 'deploy', 'run'])
        print("تم بناء APK بنجاح!")
        
    except Exception as e:
        print(f"خطأ في بناء APK: {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'apk':
        build_apk()
    else:
        build_exe()
