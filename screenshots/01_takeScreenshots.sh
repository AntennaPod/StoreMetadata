#!/bin/bash
set -e

export JAVA_HOME=/usr/lib/jvm/java-17-openjdk

cleanup() {
    adb devices | grep emulator | cut -f1 | while read line; do adb -s $line emu kill && sleep 5; done
    $ANDROID_HOME/cmdline-tools/latest/bin/avdmanager delete avd -n "AntennaPodScreenshots" || true
    rm nohup.out || true
}
trap cleanup INT TERM

################### Setup ###################

function setupEmulator() {
    emulatorConfig=$1
    cleanup
    echo no | $ANDROID_HOME/cmdline-tools/latest/bin/avdmanager create avd --force --name "AntennaPodScreenshots" --abi google_apis/x86_64 --package 'system-images;android-31;google_apis;x86_64'
    echo "
disk.dataPartition.size=6G
hw.battery=yes
hw.cpu.ncore=4
hw.ramSize=1536
showDeviceFrame=no
$emulatorConfig
    " >> $HOME/.android/avd/AntennaPodScreenshots.avd/config.ini
    nohup $ANDROID_HOME/emulator/emulator -avd AntennaPodScreenshots -no-snapshot &
    while [ "$(adb shell getprop sys.boot_completed)" != "1" ]
    do
    echo "Waiting for emulator"
    sleep 3
    done
    sleep 10
}

function install() {
    adb root

    adb uninstall de.danoeh.antennapod.debug || true
    ./gradlew :app:installPlayDebug
    adb shell am start -n "de.danoeh.antennapod.debug/de.danoeh.antennapod.activity.MainActivity"
    sleep 1
    adb shell am force-stop de.danoeh.antennapod.debug
    version=$(adb shell dumpsys package de.danoeh.antennapod.debug | grep versionName | cut -d'=' -f2)
    versionMajor=$(printf "%02d" $(echo $version | cut -d'.' -f1))
    versionMinor=$(printf "%02d" $(echo $version | cut -d'.' -f2))
}

function resetDatabase() {
    theme=$1
    adb shell am force-stop de.danoeh.antennapod.debug
    adb shell rm /data/data/de.danoeh.antennapod.debug/databases/Antennapod.db-journal || true
    adb push app/src/play/play/screenshots/ScreenshotsDatabaseExport.db /data/data/de.danoeh.antennapod.debug/databases/Antennapod.db
    adb shell chmod 777 /data/data/de.danoeh.antennapod.debug/databases
    adb shell chmod 777 /data/data/de.danoeh.antennapod.debug/databases/Antennapod.db
    echo "<?xml version='1.0' encoding='utf-8' standalone='yes' ?><map>
        <boolean name='prefMainActivityIsFirstLaunch' value='false' />
        <boolean name='screenshot_mode' value='true' />
        </map>" > tmp
    adb push tmp /data/data/de.danoeh.antennapod.debug/shared_prefs/MainActivityPrefs.xml
    echo "<?xml version='1.0' encoding='utf-8' standalone='yes' ?><map>
        <string name='prefTheme'>$theme</string>
        <long name='de.danoeh.antennapod.preferences.currentlyPlayingMedia' value='1' />
        <long name='de.danoeh.antennapod.preferences.lastPlayedFeedMediaId' value='2432' />
        <boolean name='prefEpisodeCover' value='false' />
        <string name='prefAutoUpdateIntervall'>0</string>
        </map>" > tmp
    adb push tmp /data/data/de.danoeh.antennapod.debug/shared_prefs/de.danoeh.antennapod.debug_preferences.xml
    rm tmp
    sleep 1
}

function screenshot() {
    filename=$1
    sleep 8
    adb exec-out screencap -p > $filename
}

function switchLanguage() {
    language=$1
    adb shell "setprop persist.sys.locale $language; setprop ctl.restart zygote"
    sleep 10
    adb shell settings put global sysui_demo_allowed 1
    adb shell am broadcast -a com.android.systemui.demo -e command enter
    adb shell am broadcast -a com.android.systemui.demo -e command clock -e hhmm $versionMajor$versionMinor
    adb shell am broadcast -a com.android.systemui.demo -e command notifications -e visible false
    adb shell am broadcast -a com.android.systemui.demo -e command network -e wifi show --es fully true -e level 4
    adb shell am broadcast -a com.android.systemui.demo -e command network -e mobile show -e datatype lte -e level 4
    adb shell am broadcast -a com.android.systemui.demo -e command battery -e level 100 -e plugged false
    sleep 2
}

function createScreenshots() {
    language=$1
    screnshotPrefix=$2
    folder="app/src/main/play/screenshots/raw"
    mkdir -p "$folder/$language"
    switchLanguage $language

    resetDatabase 0
    adb shell am start -n "de.danoeh.antennapod.debug/de.danoeh.antennapod.activity.MainActivity" --es "fragment_tag" "SubscriptionFragment"
    screenshot "$folder/$language/${screnshotPrefix}00.png"

    resetDatabase 0
    adb shell am start -n "de.danoeh.antennapod.debug/de.danoeh.antennapod.activity.MainActivity" --es "fragment_tag" "QueueFragment"
    sleep 1
    adb shell am start -n "de.danoeh.antennapod.debug/de.danoeh.antennapod.activity.MainActivity" --ez "open_player" "true"
    screenshot "$folder/$language/${screnshotPrefix}01.png"

    resetDatabase 0
    adb shell am start -n "de.danoeh.antennapod.debug/de.danoeh.antennapod.activity.MainActivity" --es "fragment_tag" "HomeFragment"
    screenshot "$folder/$language/${screnshotPrefix}02.png"

    resetDatabase 0
    adb shell am start -n "de.danoeh.antennapod.debug/de.danoeh.antennapod.activity.MainActivity" --es "fragment_tag" "EpisodesFragment"
    screenshot "$folder/$language/${screnshotPrefix}03a.png"

    resetDatabase 1
    adb shell am start -n "de.danoeh.antennapod.debug/de.danoeh.antennapod.activity.MainActivity" --es "fragment_tag" "EpisodesFragment"
    screenshot "$folder/$language/${screnshotPrefix}03b.png"

    resetDatabase 0
    adb shell am start -n "de.danoeh.antennapod.debug/de.danoeh.antennapod.activity.MainActivity" --es "fragment_tag" "QueueFragment"
    screenshot "$folder/$language/${screnshotPrefix}04.png"

    resetDatabase 0
    adb shell am start -n "de.danoeh.antennapod.debug/de.danoeh.antennapod.activity.MainActivity" --es "fragment_tag" "AddFeedFragment"
    screenshot "$folder/$language/${screnshotPrefix}05.png"
}

################### Create screenshots ###################

function createScreenshotsAllLanguages() {
    screnshotPrefix=$1
    createScreenshots "en-US" "$screnshotPrefix"
    createScreenshots "de-DE" "$screnshotPrefix"
    createScreenshots "es-ES" "$screnshotPrefix"
    createScreenshots "fr-FR" "$screnshotPrefix"
    createScreenshots "he-IL" "$screnshotPrefix"
    createScreenshots "it-IT" "$screnshotPrefix"
    createScreenshots "nl-NL" "$screnshotPrefix"
}

setupEmulator "
hw.lcd.density=420
hw.lcd.width=1080
hw.lcd.height=1920"
install
createScreenshotsAllLanguages ""
cleanup

setupEmulator "
hw.lcd.density=320
hw.lcd.height=1920
hw.lcd.width=1200"
install
createScreenshotsAllLanguages "tablet-7-"
cleanup

setupEmulator "
hw.lcd.density=320
hw.lcd.height=1600
hw.lcd.width=2560"
install
createScreenshotsAllLanguages "tablet-10-"
cleanup

