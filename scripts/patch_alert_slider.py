from pathlib import Path

base = Path("/serverhive5/raizenftw/aospa/hardware/oplus/packages/KeyHandler")

def rep(path, old, new):
    p = base / path
    t = p.read_text()
    assert t.count(old) == 1, (path, t.count(old))
    p.write_text(t.replace(old, new, 1))
    print("patched", path)

rep(
    "src/org/lineageos/settings/device/KeyHandler.kt",
    "        val muteMedia = sharedPreferences.getBoolean(MUTE_MEDIA_WITH_SILENT, false)\n"
    "        val showDialog = sharedPreferences.getBoolean(SHOW_DIALOG, true)\n",
    "        val muteMedia = sharedPreferences.getBoolean(MUTE_MEDIA_WITH_SILENT, false)\n",
)

rep(
    "src/org/lineageos/settings/device/KeyHandler.kt",
    "            if (!firstRun) {\n"
    "                if (showDialog) sendNotification(position, mode)\n"
    "                vibrateIfNeeded(mode)\n"
    "            }\n",
    "            if (!firstRun) {\n"
    "                vibrateIfNeeded(mode)\n"
    "            }\n",
)

rep(
    "res/xml/button_panel.xml",
    "\n"
    "        <SwitchPreferenceCompat\n"
    "            android:key=\"config_show_dialog\"\n"
    "            android:title=\"@string/alert_slider_notification_dialog_title\"\n"
    "            android:summary=\"@string/alert_slider_notification_dialog_summary\"\n"
    "            android:defaultValue=\"true\" />\n",
    "",
)

rep(
    "AndroidManifest.xml",
    "\n"
    "        <service\n"
    "            android:name=\".AlertSliderPlugin\"\n"
    "            android:permission=\"com.android.systemui.permission.PLUGIN\"\n"
    "            android:exported=\"true\">\n"
    "            <intent-filter>\n"
    "                <action android:name=\"com.android.systemui.action.PLUGIN_OVERLAY\" />\n"
    "            </intent-filter>\n"
    "        </service>\n",
    "",
)
