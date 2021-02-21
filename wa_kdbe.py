import argparse
import concurrent.futures
import os
import platform
import re
import subprocess
import time

import helpers.ADBDeviceSerialId as deviceId
import helpers.TCPDeviceSerialId as tcpDeviceId
from helpers.CustomCI import CustomInput, CustomPrint
from helpers.LinuxUSB import LinuxUSB
from helpers.WIndowsUSB import WindowsUSB
from view_extract import ExtractAB

# Detect OS
isWindows = False
isLinux = False
if platform.system() == 'Windows':
    isWindows = True
if platform.system() == 'Linux':
    isLinux = True

# Global Variables
appURLWhatsAppCDN = 'https://www.cdn.whatsapp.net/android/2.11.431/WhatsApp.apk'
appURLWhatsCryptCDN = 'https://whatcrypt.com/WhatsApp-2.11.431.apk'
isJAVAInstalled = False


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    CheckBin()
    ShowBanner()
    global isJAVAInstalled
    isJAVAInstalled = CheckJAVA()
    print('\n')
    readInstruction = CustomInput(
        '\aPlease read above instructions carefully \u2191 . Continue? (default y) : ', 'yellow') or 'y'
    if(readInstruction.upper() == 'Y'):
        USBMode()
    else:
        Exit()


def BackupWhatsAppApk(SDKVersion, versionName, WhatsAppapkPath):
    os.system(adb + ' shell am force-stop com.whatsapp') if(SDKVersion >
                                                            11) else os.system(adb + ' shell am kill com.whatsapp')
    if (isFast):
        CustomPrint('Backing up WhatsApp ' + versionName +
                    ' apk, the one installed on device to /sdcard/WhatsAppbackup.apk', 'yellow')
        os.system(adb + ' shell cp ' + WhatsAppapkPath +
                  ' sdcard/WhatsAppbackup.apk')
        CustomPrint('Apk backup complete.')
    else:
        CustomPrint('Backing up WhatsApp ' + versionName +
                    ' apk, the one installed on device to ' + tmp + 'WhatsAppbackup.apk', 'yellow')
        os.mkdir(tmp) if not (os.path.isdir(tmp)) else CustomPrint(
            'Folder ' + tmp + ' already exists.', 'yellow')
        os.system(adb + ' pull ' + WhatsAppapkPath +
                  ' ' + tmp + 'WhatsAppbackup.apk')
        CustomPrint('Apk backup complete.')


def BackupWhatsAppDataasAb(SDKVersion):
    CustomPrint('Backing up WhatsApp data as ' + tmp +
                'whatsapp.ab. May take time, don\'t panic.')
    try:
        os.system(adb + ' backup -f ' + tmp + 'whatsapp.ab com.whatsapp') if(SDKVersion >=
                                                                             23) else os.system(adb + ' backup -f ' + tmp + 'whatsapp.ab -noapk com.whatsapp')
    except Exception as e:
        CustomPrint(e, 'red')
    CustomPrint('Done backing up data. Size : ' +
                str(os.path.getsize(tmp + 'whatsapp.ab')) + ' bytes.')


def CheckBin():
    if (not os.path.isdir('bin')):
        CustomPrint('I can not find bin folder, check again...', 'red')
        Exit()
    pass


def CheckJAVA():
    JAVAVersion = re.search('(?<=version ")(.*)(?=")', str(subprocess.check_output(
        'java -version'.split(), stderr=subprocess.STDOUT))).group(1)
    isJAVAInstalled = True if(JAVAVersion) else False
    if (isJAVAInstalled):
        CustomPrint('Found Java installed on system.')
        return isJAVAInstalled
    else:
        noJAVAContinue = CustomInput(
            'It looks like you don\'t have JAVA installed on your system. Would you like to (C)ontinue with the process and \'view extract\' later? or (S)top? : ', 'red') or 'c'
        if(noJAVAContinue.upper() == 'C'):
            CustomPrint(
                'Continuing without JAVA, once JAVA is installed on system run \'view_extract.py\'', 'yellow')
            return isJAVAInstalled
        else:
            Exit()


def Exit():
    print('\n')
    CustomPrint('Exiting...')
    os.system(
        'bin\\adb.exe kill-server') if(isWindows) else os.system('adb kill-server')
    quit()


def InstallLegacy(SDKVersion):
    CustomPrint('Installing legacy WhatsApp V2.11.431, hold tight now.')
    if(SDKVersion >= 17):
        os.system(adb + ' install -r -d ' + helpers + 'LegacyWhatsApp.apk')
    else:
        os.system(adb + ' install -r ' + helpers + 'LegacyWhatsApp.apk')
    CustomPrint('Installation Complete.')


def RealDeal(SDKVersion, WhatsAppapkPath, versionName, sdPath):
    BackupWhatsAppApk(SDKVersion, versionName, WhatsAppapkPath)
    UninstallWhatsApp(SDKVersion)
    # Reboot here.
    if(isAllowReboot):
        if(not tcpIP):
            print('\n')
            CustomPrint('Rebooting device, please wait.', 'yellow')
            os.system(adb + ' reboot')
            while(subprocess.getoutput(adb + ' get-state') != 'device'):
                CustomPrint('Waiting for device...')
                time.sleep(5)
            CustomInput('Press any key after unlocking device.', 'yellow')
        else:
            CustomPrint(
                'Rebooting device in TCP mode break the connection and won\'t work until explicitly turned on in device and/or in PC. Skipping...', 'yellow')

    InstallLegacy(SDKVersion)
    # Before backup run app
    os.system(adb + ' shell am start -n com.whatsapp/.Main')
    CustomInput(
        '\aPress any key after running Legacy WhatsApp for a while.', 'yellow')
    BackupWhatsAppDataasAb(SDKVersion)
    ReinstallWhatsApp()
    print('\n')
    CustomPrint(
        '\aOur work with device has finished, it is safe to remove it now.', 'yellow')
    print('\n')
    ExtractAB(isJAVAInstalled, sdPath=sdPath, ADBSerialId=ADBSerialId)


def ReinstallWhatsApp():
    CustomPrint('Reinstallting original WhatsApp.')
    if(isFast):
        try:
            os.system(adb + ' install -r -d /sdcard/WhatsAppbackup.apk')
        except Exception as e:
            CustomPrint(e, 'red')
            CustomPrint(
                'Could not install WhatsApp, install using Play Store.\nHowever if it crashes then you have to clear storage/clear data from settings => app settings => WhatsApp.')
    else:
        try:
            os.system(adb + ' install -r -d ' + tmp +
                      'WhatsAppbackup.apk')
        except Exception as e:
            CustomPrint(e, 'red')
            CustomPrint('Could not install WhatsApp, install by running \'restore_whatsapp.py\' or manually installing from Play Store.\nHowever if it crashes then you have to clear storage/clear data from settings => app settings => WhatsApp.')


def RunScrCpy(_isScrCpy):
    if(_isScrCpy and isWindows):
        cmd = 'bin\scrcpy.exe'
        proc = subprocess.Popen(cmd.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, shell=False)
        proc.communicate()


def ShowBanner():
    banner_path = 'non_essentials/banner.txt'
    try:
        banner = open(banner_path, 'r')
        banner_content = banner.read()
        CustomPrint(banner_content, 'green', ['bold'], False)
        banner.close()
    except Exception as e:
        CustomPrint(e, 'red')
    CustomPrint('============ WhatsApp Key / Database Extrator for non-rooted Android ===========\n',
                'green', ['bold'], False)
    intro_path = 'non_essentials/intro.txt'
    try:
        intro = open(intro_path, 'r')
        intro_content = intro.read()
        CustomPrint(intro_content, 'green', ['bold'], False)
        intro.close()
    except Exception as e:
        CustomPrint(e, 'red')


def UninstallWhatsApp(SDKVersion):
    if(SDKVersion >= 23):
        try:
            CustomPrint('Uninstalling WhatsApp, skipping data.')
            os.system(adb + ' shell pm uninstall -k com.whatsapp')
            CustomPrint('Uninstalled.')
        except Exception as e:
            CustomPrint('Could not uninstall WhatsApp.')
            CustomPrint(e, 'red')
            Exit()


def USBMode():
    if(isWindows):
        ACReturnCode, SDKVersion, WhatsAppapkPath, versionName, sdPath = WindowsUSB(
            adb)
        RealDeal(SDKVersion, WhatsAppapkPath, versionName,
                 sdPath) if ACReturnCode == 1 else Exit()
    else:
        ACReturnCode, SDKVersion, WhatsAppapkPath, versionName, sdPath = LinuxUSB(
            ADBSerialId)
        RealDeal(SDKVersion, WhatsAppapkPath, versionName,
                 sdPath) if ACReturnCode == 1 else Exit()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--allow-reboot', action='store_true',
                        help='Allow reboot of device before installation of LegacyWhatsApp.apk to prevent some issues like [INSTALL_FAILED_VERSION_DOWNGRADE]')
    parser.add_argument(
        '--tcp-ip', help='Connects to a remote device via TCP mode.')
    parser.add_argument(
        '--tcp-port', help='Port number to connect to. Default : 5555')
    parser.add_argument('--scrcpy', action='store_true',
                        help='Run ScrCpy to see and control Android device.')
    parser.add_argument('--fast', action='store_true',
                        help='Try to speed up process by taking apk backup inside phone and reinstalling from there.')
    args = parser.parse_args()
    #args = parser.parse_args('--fast --scrcpy'.split())

    isAllowReboot = args.allow_reboot
    tcpIP = args.tcp_ip
    tcpPort = args.tcp_port
    isScrCpy = args.scrcpy
    isFast = args.fast
    if(tcpIP):
        if(not tcpPort):
            tcpPort = '5555'
        ADBSerialId = tcpDeviceId.init(tcpIP, tcpPort)
    else:
        ADBSerialId = deviceId.init()
    if(not ADBSerialId):
        quit()

    # Global command line helpers
    adb = 'bin\\adb.exe -s ' + ADBSerialId
    tmp = 'tmp/'
    grep = 'bin\\grep.exe'
    curl = 'bin\\curl.exe'
    helpers = 'helpers/'
    if(isLinux):
        adb = 'adb -s ' + ADBSerialId
        grep = 'grep'
        curl = 'curl'

    with concurrent.futures.ThreadPoolExecutor() as executor:
        f1 = executor.submit(main)
        time.sleep(1)
        f2 = executor.submit(RunScrCpy, isScrCpy)
