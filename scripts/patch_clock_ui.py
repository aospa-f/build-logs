from pathlib import Path

base = Path("/serverhive5/raizenftw/aospa")

def write(path, content):
    p = base / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    print("wrote", path)

def rep(path, old, new):
    p = base / path
    t = p.read_text()
    assert t.count(old) == 1, (path, t.count(old))
    p.write_text(t.replace(old, new, 1))
    print("patched", path)

write(
    "packages/apps/ParanoidSettings/res/xml/status_bar_clock_settings.xml",
    '''<?xml version="1.0" encoding="utf-8"?>
<!--
     SPDX-FileCopyrightText: 2026 The AOSPA Project
     SPDX-License-Identifier: Apache-2.0
-->
<PreferenceScreen xmlns:android="http://schemas.android.com/apk/res/android"
    android:title="@string/status_bar_clock_title">

    <SwitchPreferenceCompat
        android:key="clock_seconds"
        android:title="@string/status_bar_clock_show_seconds_title"
        android:summary="@string/status_bar_clock_show_seconds_summary"
        android:defaultValue="false"
        android:persistent="false" />

    <ListPreference
        android:key="status_bar_clock_am_pm"
        android:title="@string/status_bar_clock_am_pm_title"
        android:entries="@array/status_bar_clock_am_pm_entries"
        android:entryValues="@array/status_bar_clock_am_pm_values"
        android:defaultValue="2"
        android:persistent="false" />

    <ListPreference
        android:key="status_bar_clock_date_display"
        android:title="@string/status_bar_clock_date_display_title"
        android:entries="@array/status_bar_clock_date_display_entries"
        android:entryValues="@array/status_bar_clock_date_display_values"
        android:defaultValue="0"
        android:persistent="false" />

    <ListPreference
        android:key="status_bar_clock_date_style"
        android:title="@string/status_bar_clock_date_style_title"
        android:entries="@array/status_bar_clock_date_style_entries"
        android:entryValues="@array/status_bar_clock_date_style_values"
        android:defaultValue="0"
        android:persistent="false" />

    <ListPreference
        android:key="status_bar_clock_date_position"
        android:title="@string/status_bar_clock_date_position_title"
        android:entries="@array/status_bar_clock_date_position_entries"
        android:entryValues="@array/status_bar_clock_date_position_values"
        android:defaultValue="0"
        android:persistent="false" />

    <EditTextPreference
        android:key="status_bar_clock_date_format"
        android:title="@string/status_bar_clock_date_format_title"
        android:dialogMessage="@string/status_bar_clock_date_format_message"
        android:defaultValue=""
        android:persistent="false" />

    <SwitchPreferenceCompat
        android:key="status_bar_clock_bold"
        android:title="@string/status_bar_clock_bold_title"
        android:summary="@string/status_bar_clock_bold_summary"
        android:defaultValue="false"
        android:persistent="false" />

    <SwitchPreferenceCompat
        android:key="status_bar_clock_period_separator"
        android:title="@string/status_bar_clock_period_separator_title"
        android:summary="@string/status_bar_clock_period_separator_summary"
        android:defaultValue="false"
        android:persistent="false" />

</PreferenceScreen>
''',
)

write(
    "packages/apps/ParanoidSettings/src/co/aospa/settings/display/StatusBarClockSettings.java",
    '''/*
 * SPDX-FileCopyrightText: 2026 The AOSPA Project
 * SPDX-License-Identifier: Apache-2.0
 */

package co.aospa.settings.display;

import android.os.Bundle;
import android.os.UserHandle;
import android.provider.Settings;

import androidx.preference.EditTextPreference;
import androidx.preference.ListPreference;
import androidx.preference.SwitchPreferenceCompat;

import com.android.settings.R;
import com.android.settings.SettingsPreferenceFragment;
import com.android.settings.search.BaseSearchIndexProvider;
import com.android.settingslib.search.SearchIndexable;

@SearchIndexable
public class StatusBarClockSettings extends SettingsPreferenceFragment {

    private static final String KEY_SECONDS = "clock_seconds";
    private static final String KEY_AM_PM = "status_bar_clock_am_pm";
    private static final String KEY_DATE_DISPLAY = "status_bar_clock_date_display";
    private static final String KEY_DATE_STYLE = "status_bar_clock_date_style";
    private static final String KEY_DATE_POSITION = "status_bar_clock_date_position";
    private static final String KEY_DATE_FORMAT = "status_bar_clock_date_format";
    private static final String KEY_BOLD = "status_bar_clock_bold";
    private static final String KEY_PERIOD_SEPARATOR = "status_bar_clock_period_separator";

    @Override
    public void onCreatePreferences(Bundle savedInstanceState, String rootKey) {
        setPreferencesFromResource(R.xml.status_bar_clock_settings, rootKey);

        bindSwitch(KEY_SECONDS, KEY_SECONDS, false);
        bindList(KEY_AM_PM, KEY_AM_PM, 2);
        bindList(KEY_DATE_DISPLAY, KEY_DATE_DISPLAY, 0);
        bindList(KEY_DATE_STYLE, KEY_DATE_STYLE, 0);
        bindList(KEY_DATE_POSITION, KEY_DATE_POSITION, 0);
        bindDateFormat();
        bindSwitch(KEY_BOLD, KEY_BOLD, false);
        bindSwitch(KEY_PERIOD_SEPARATOR, KEY_PERIOD_SEPARATOR, false);
    }

    private void bindSwitch(String preferenceKey, String settingKey, boolean defaultValue) {
        SwitchPreferenceCompat preference = findPreference(preferenceKey);
        if (preference == null) {
            return;
        }
        boolean value = Settings.Secure.getIntForUser(getContentResolver(), settingKey,
                defaultValue ? 1 : 0, UserHandle.USER_CURRENT) != 0;
        preference.setChecked(value);
        preference.setOnPreferenceChangeListener((pref, newValue) -> {
            boolean checked = (Boolean) newValue;
            Settings.Secure.putIntForUser(getContentResolver(), settingKey,
                    checked ? 1 : 0, UserHandle.USER_CURRENT);
            return true;
        });
    }

    private void bindList(String preferenceKey, String settingKey, int defaultValue) {
        ListPreference preference = findPreference(preferenceKey);
        if (preference == null) {
            return;
        }
        int value = Settings.Secure.getIntForUser(getContentResolver(), settingKey,
                defaultValue, UserHandle.USER_CURRENT);
        preference.setValue(String.valueOf(value));
        updateListSummary(preference, String.valueOf(value));
        preference.setOnPreferenceChangeListener((pref, newValue) -> {
            String valueString = (String) newValue;
            Settings.Secure.putIntForUser(getContentResolver(), settingKey,
                    Integer.parseInt(valueString), UserHandle.USER_CURRENT);
            updateListSummary((ListPreference) pref, valueString);
            return true;
        });
    }

    private void updateListSummary(ListPreference preference, String value) {
        int index = preference.findIndexOfValue(value);
        if (index >= 0 && index < preference.getEntries().length) {
            preference.setSummary(preference.getEntries()[index]);
        }
    }

    private void bindDateFormat() {
        EditTextPreference preference = findPreference(KEY_DATE_FORMAT);
        if (preference == null) {
            return;
        }
        String value = Settings.Secure.getStringForUser(getContentResolver(), KEY_DATE_FORMAT,
                UserHandle.USER_CURRENT);
        if (value == null) {
            value = "";
        }
        preference.setText(value);
        updateDateFormatSummary(preference, value);
        preference.setOnPreferenceChangeListener((pref, newValue) -> {
            String valueString = newValue == null ? "" : newValue.toString();
            Settings.Secure.putStringForUser(getContentResolver(), KEY_DATE_FORMAT,
                    valueString, UserHandle.USER_CURRENT);
            updateDateFormatSummary((EditTextPreference) pref, valueString);
            return true;
        });
    }

    private void updateDateFormatSummary(EditTextPreference preference, String value) {
        preference.setSummary(value.isEmpty()
                ? getString(R.string.status_bar_clock_date_format_default)
                : value);
    }

    @Override
    public int getMetricsCategory() {
        return -1;
    }

    public static final BaseSearchIndexProvider SEARCH_INDEX_DATA_PROVIDER =
            new BaseSearchIndexProvider(R.xml.status_bar_clock_settings);
}
''',
)

write(
    "packages/apps/ParanoidSettings/src/co/aospa/settings/display/StatusBarClockPreferenceController.java",
    '''/*
 * SPDX-FileCopyrightText: 2026 The AOSPA Project
 * SPDX-License-Identifier: Apache-2.0
 */

package co.aospa.settings.display;

import android.content.Context;

import com.android.settings.R;
import com.android.settings.core.BasePreferenceController;

public class StatusBarClockPreferenceController extends BasePreferenceController {

    public StatusBarClockPreferenceController(Context context, String preferenceKey) {
        super(context, preferenceKey);
    }

    @Override
    public int getAvailabilityStatus() {
        return AVAILABLE;
    }

    @Override
    public CharSequence getSummary() {
        return mContext.getString(R.string.status_bar_clock_summary);
    }
}
''',
)

rep(
    "packages/apps/ParanoidSettings/res/values/aospa_strings.xml",
    "</resources>\n",
    '''
    <!-- Status bar clock and date -->
    <string name="status_bar_clock_title">Clock and date</string>
    <string name="status_bar_clock_summary">Show seconds, date, AM/PM and styling in the status bar</string>
    <string name="keywords_status_bar_clock">clock, date, seconds, am/pm, bold, status bar</string>
    <string name="status_bar_clock_show_seconds_title">Show seconds</string>
    <string name="status_bar_clock_show_seconds_summary">Show seconds in the status bar clock</string>
    <string name="status_bar_clock_am_pm_title">AM/PM style</string>
    <string name="status_bar_clock_date_display_title">Show date</string>
    <string name="status_bar_clock_date_style_title">Date case</string>
    <string name="status_bar_clock_date_position_title">Date position</string>
    <string name="status_bar_clock_date_format_title">Date format</string>
    <string name="status_bar_clock_date_format_default">EEE</string>
    <string name="status_bar_clock_date_format_message">Java SimpleDateFormat pattern. Leave empty to use EEE (for example: Mon).</string>
    <string name="status_bar_clock_bold_title">Bold clock</string>
    <string name="status_bar_clock_bold_summary">Use a bold typeface for the status bar clock</string>
    <string name="status_bar_clock_period_separator_title">Period separator</string>
    <string name="status_bar_clock_period_separator_summary">Replace the colon in the clock with a period</string>

</resources>
''',
)

rep(
    "packages/apps/ParanoidSettings/res/values/aospa_arrays.xml",
    "</resources>\n",
    '''
    <!-- Status bar clock and date -->
    <string-array name="status_bar_clock_am_pm_entries">
        <item>Normal</item>
        <item>Small</item>
        <item>Hidden</item>
    </string-array>
    <string-array name="status_bar_clock_am_pm_values">
        <item>0</item>
        <item>1</item>
        <item>2</item>
    </string-array>
    <string-array name="status_bar_clock_date_display_entries">
        <item>Hidden</item>
        <item>Small</item>
        <item>Normal</item>
    </string-array>
    <string-array name="status_bar_clock_date_display_values">
        <item>0</item>
        <item>1</item>
        <item>2</item>
    </string-array>
    <string-array name="status_bar_clock_date_style_entries">
        <item>Regular</item>
        <item>Lowercase</item>
        <item>UPPERCASE</item>
    </string-array>
    <string-array name="status_bar_clock_date_style_values">
        <item>0</item>
        <item>1</item>
        <item>2</item>
    </string-array>
    <string-array name="status_bar_clock_date_position_entries">
        <item>Before time</item>
        <item>After time</item>
    </string-array>
    <string-array name="status_bar_clock_date_position_values">
        <item>0</item>
        <item>1</item>
    </string-array>

</resources>
''',
)

rep(
    "packages/apps/Settings/res/xml/display_settings.xml",
    '''        <Preference
            android:key="refresh_rate"
            android:title="@string/refresh_rate_title"
            android:summary="@string/summary_placeholder"
            android:fragment="co.aospa.settings.display.RefreshRateSettings"
            settings:keywords="@string/keywords_refresh_rate"
            settings:controller="co.aospa.settings.display.RefreshRatePreferenceController"/>
''',
    '''        <Preference
            android:key="refresh_rate"
            android:title="@string/refresh_rate_title"
            android:summary="@string/summary_placeholder"
            android:fragment="co.aospa.settings.display.RefreshRateSettings"
            settings:keywords="@string/keywords_refresh_rate"
            settings:controller="co.aospa.settings.display.RefreshRatePreferenceController"/>

        <Preference
            android:key="status_bar_clock"
            android:title="@string/status_bar_clock_title"
            android:summary="@string/status_bar_clock_summary"
            android:fragment="co.aospa.settings.display.StatusBarClockSettings"
            settings:keywords="@string/keywords_status_bar_clock"
            settings:controller="co.aospa.settings.display.StatusBarClockPreferenceController"/>
''',
)
