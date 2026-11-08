from pathlib import Path

base = Path("/serverhive5/raizenftw/aospa")

def rep(path, old, new):
    p = base / path
    t = p.read_text()
    assert t.count(old) == 1, (path, t.count(old))
    p.write_text(t.replace(old, new, 1))
    print("patched", path)

# Strings
rep(
    "packages/apps/ParanoidSettings/res/values/aospa_strings.xml",
    "</resources>\n",
    '''
    <!-- Screen off music/volume gestures -->
    <string name="gestures_volume_up">Volume up</string>
    <string name="gestures_volume_down">Volume down</string>
    <string name="offscreen_gesture_music_apps_title">Music apps</string>
    <string name="offscreen_gesture_music_apps_summary">Only respond to music and volume gestures when one of these apps is playing</string>
    <string name="offscreen_gesture_music_apps_all">All media apps</string>
    <string name="offscreen_gesture_music_apps_selected">%d selected</string>

</resources>
''',
)

# Arrays: add volume actions to the generic gesture arrays
rep(
    "packages/apps/ParanoidSettings/res/values/aospa_arrays.xml",
    "        <item>@string/gestures_open_dialer</item>\n"
    "    </string-array>\n",
    "        <item>@string/gestures_open_dialer</item>\n"
    "        <item>@string/gestures_volume_up</item>\n"
    "        <item>@string/gestures_volume_down</item>\n"
    "    </string-array>\n",
)
rep(
    "packages/apps/ParanoidSettings/res/values/aospa_arrays.xml",
    "        <item>9</item>\n"
    "    </string-array>\n",
    "        <item>9</item>\n"
    "        <item>10</item>\n"
    "        <item>11</item>\n"
    "    </string-array>\n",
)

# Add the multi-select preference to the screen off gesture screen
rep(
    "packages/apps/ParanoidSettings/res/xml/offscreen_gesture_settings.xml",
    "</PreferenceScreen>\n",
    '''
    <MultiSelectListPreference
        android:key="offscreen_gesture_music_apps"
        android:title="@string/offscreen_gesture_music_apps_title"
        android:summary="@string/offscreen_gesture_music_apps_summary"
        android:persistent="false" />

</PreferenceScreen>
''',
)

# Settings fragment imports
rep(
    "packages/apps/ParanoidSettings/src/co/aospa/settings/gestures/OffscreenGestureSettings.java",
    "import android.content.Context;\n"
    "import android.os.Bundle;\n",
    "import android.content.Context;\n"
    "import android.content.Intent;\n"
    "import android.content.pm.PackageManager;\n"
    "import android.content.pm.ResolveInfo;\n"
    "import android.media.browse.MediaBrowserService;\n"
    "import android.os.Bundle;\n",
)
rep(
    "packages/apps/ParanoidSettings/src/co/aospa/settings/gestures/OffscreenGestureSettings.java",
    "import android.os.UserHandle;\n"
    "import android.provider.SearchIndexableResource;\n"
    "import android.provider.Settings;\n",
    "import android.os.UserHandle;\n"
    "import android.provider.SearchIndexableResource;\n"
    "import android.provider.Settings;\n"
    "import android.text.TextUtils;\n",
)
rep(
    "packages/apps/ParanoidSettings/src/co/aospa/settings/gestures/OffscreenGestureSettings.java",
    "import androidx.preference.ListPreference;\n",
    "import androidx.preference.ListPreference;\n"
    "import androidx.preference.MultiSelectListPreference;\n",
)
rep(
    "packages/apps/ParanoidSettings/src/co/aospa/settings/gestures/OffscreenGestureSettings.java",
    "import java.util.ArrayList;\n"
    "import java.util.Collections;\n"
    "import java.util.HashMap;\n"
    "import java.util.List;\n",
    "import java.util.ArrayList;\n"
    "import java.util.Collections;\n"
    "import java.util.HashMap;\n"
    "import java.util.HashSet;\n"
    "import java.util.List;\n"
    "import java.util.Map;\n"
    "import java.util.Set;\n"
    "import java.util.TreeMap;\n",
)

# Add constant
rep(
    "packages/apps/ParanoidSettings/src/co/aospa/settings/gestures/OffscreenGestureSettings.java",
    "    private static final String KEY_TWO_FINGER_SWIPE = \"two_finger_swipe\";\n",
    "    private static final String KEY_TWO_FINGER_SWIPE = \"two_finger_swipe\";\n"
    "    private static final String KEY_MUSIC_APPS = \"offscreen_gesture_music_apps\";\n",
)

# Call setup after gesture loop
rep(
    "packages/apps/ParanoidSettings/src/co/aospa/settings/gestures/OffscreenGestureSettings.java",
    "            } else {\n"
    "                removePreference(gestureKey);\n"
    "            }\n"
    "        }\n"
    "    }\n",
    "            } else {\n"
    "                removePreference(gestureKey);\n"
    "            }\n"
    "        }\n"
    "        setupMusicAppsPreference();\n"
    "    }\n",
)

# Add method before onDestroyView
rep(
    "packages/apps/ParanoidSettings/src/co/aospa/settings/gestures/OffscreenGestureSettings.java",
    "    @Override\n"
    "    public void onDestroyView() {\n",
    "    private void setupMusicAppsPreference() {\n"
    "        MultiSelectListPreference preference = findPreference(KEY_MUSIC_APPS);\n"
    "        if (preference == null) {\n"
    "            return;\n"
    "        }\n"
    "\n"
    "        final Context context = requireContext();\n"
    "        final PackageManager packageManager = context.getPackageManager();\n"
    "        final Map<String, String> apps = new TreeMap<>(String.CASE_INSENSITIVE_ORDER);\n"
    "\n"
    "        final Intent browserIntent = new Intent(MediaBrowserService.SERVICE_INTERFACE);\n"
    "        for (ResolveInfo info : packageManager.queryIntentServices(\n"
    "                browserIntent, PackageManager.MATCH_ALL)) {\n"
    "            if (info.serviceInfo == null) {\n"
    "                continue;\n"
    "            }\n"
    "            final String pkg = info.serviceInfo.packageName;\n"
    "            if (context.getPackageName().equals(pkg)) {\n"
    "                continue;\n"
    "            }\n"
    "            final CharSequence label = info.serviceInfo.loadLabel(packageManager);\n"
    "            apps.put(pkg, label != null ? label.toString() : pkg);\n"
    "        }\n"
    "\n"
    "        final Intent musicIntent = new Intent(Intent.ACTION_VIEW);\n"
    "        musicIntent.setType(\"audio/*\");\n"
    "        musicIntent.addCategory(Intent.CATEGORY_DEFAULT);\n"
    "        for (ResolveInfo info : packageManager.queryIntentActivities(\n"
    "                musicIntent, PackageManager.MATCH_ALL)) {\n"
    "            if (info.activityInfo == null) {\n"
    "                continue;\n"
    "            }\n"
    "            final String pkg = info.activityInfo.packageName;\n"
    "            if (context.getPackageName().equals(pkg)) {\n"
    "                continue;\n"
    "            }\n"
    "            final CharSequence label = info.activityInfo.loadLabel(packageManager);\n"
    "            apps.putIfAbsent(pkg, label != null ? label.toString() : pkg);\n"
    "        }\n"
    "\n"
    "        if (apps.isEmpty()) {\n"
    "            getPreferenceScreen().removePreference(preference);\n"
    "            return;\n"
    "        }\n"
    "\n"
    "        final List<Map.Entry<String, String>> entries = new ArrayList<>(apps.entrySet());\n"
    "        entries.sort(Map.Entry.comparingByValue(String.CASE_INSENSITIVE_ORDER));\n"
    "        final CharSequence[] labels = new CharSequence[entries.size()];\n"
    "        final CharSequence[] values = new CharSequence[entries.size()];\n"
    "        for (int i = 0; i < entries.size(); i++) {\n"
    "            values[i] = entries.get(i).getKey();\n"
    "            labels[i] = entries.get(i).getValue();\n"
    "        }\n"
    "        preference.setEntries(labels);\n"
    "        preference.setEntryValues(values);\n"
    "\n"
    "        final String stored = Settings.System.getStringForUser(\n"
    "                context.getContentResolver(), KEY_MUSIC_APPS, UserHandle.USER_CURRENT);\n"
    "        final Set<String> selected = new HashSet<>();\n"
    "        if (!TextUtils.isEmpty(stored)) {\n"
    "            for (String pkg : stored.split(\",\")) {\n"
    "                if (apps.containsKey(pkg)) {\n"
    "                    selected.add(pkg);\n"
    "                }\n"
    "            }\n"
    "        }\n"
    "        preference.setValues(selected);\n"
    "        updateMusicAppsSummary(preference, selected);\n"
    "        preference.setOnPreferenceChangeListener((pref, newValue) -> {\n"
    "            @SuppressWarnings(\"unchecked\")\n"
    "            final Set<String> selectedValues = (Set<String>) newValue;\n"
    "            Settings.System.putStringForUser(context.getContentResolver(), KEY_MUSIC_APPS,\n"
    "                    TextUtils.join(\",\", selectedValues), UserHandle.USER_CURRENT);\n"
    "            updateMusicAppsSummary((MultiSelectListPreference) pref, selectedValues);\n"
    "            return true;\n"
    "        });\n"
    "    }\n"
    "\n"
    "    private void updateMusicAppsSummary(MultiSelectListPreference preference,\n"
    "            Set<String> selected) {\n"
    "        preference.setSummary(selected.isEmpty()\n"
    "                ? getString(R.string.offscreen_gesture_music_apps_all)\n"
    "                : getString(R.string.offscreen_gesture_music_apps_selected, selected.size()));\n"
    "    }\n"
    "\n"
    "    @Override\n"
    "    public void onDestroyView() {\n",
)
