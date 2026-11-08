#!/usr/bin/env python3
"""Apply the four requested AOSPA feature changes."""

from pathlib import Path

ROOT = Path("/serverhive5/raizenftw/aospa")


def replace(path: str, old: str, new: str) -> None:
    p = ROOT / path
    text = p.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one match in {path}, found {count}")
    p.write_text(text.replace(old, new, 1))
    print(f"patched {path}")


def write(path: str, content: str) -> None:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    print(f"wrote {path}")


# ---------------------------------------------------------------------------
# frameworks/base: Settings constants
# ---------------------------------------------------------------------------
replace(
    "frameworks/base/core/java/android/provider/Settings.java",
    """        /**
         * Control whether FLAG_SECURE is ignored for all windows.
         * @hide
         */
        @Readable
        public static final String WINDOW_IGNORE_SECURE = "window_ignore_secure";

        /**
         * These entries are considered common between the personal and the managed profile,""",
    """        /**
         * Control whether FLAG_SECURE is ignored for all windows.
         * @hide
         */
        @Readable
        public static final String WINDOW_IGNORE_SECURE = "window_ignore_secure";

        /**
         * Whether screenshots should be reported to apps through the screenshot detection API.
         * @hide
         */
        @Readable
        public static final String SCREENSHOT_DETECTION = "screenshot_detection";

        /**
         * Whether Wi-Fi and Bluetooth should be turned off after five minutes without a
         * connection.
         * @hide
         */
        @Readable
        public static final String IDLE_RADIO_TIMEOUT = "idle_radio_timeout";

        /**
         * These entries are considered common between the personal and the managed profile,""",
)

# ---------------------------------------------------------------------------
# frameworks/base: BatteryStatus (charging details)
# ---------------------------------------------------------------------------
replace(
    "frameworks/base/packages/SettingsLib/src/com/android/settingslib/fuelgauge/BatteryStatus.java",
    """import static android.os.BatteryManager.EXTRA_STATUS;
import static android.os.OsProtoEnums.BATTERY_PLUGGED_NONE;""",
    """import static android.os.BatteryManager.EXTRA_STATUS;
import static android.os.BatteryManager.EXTRA_TEMPERATURE;
import static android.os.OsProtoEnums.BATTERY_PLUGGED_NONE;""",
)

replace(
    "frameworks/base/packages/SettingsLib/src/com/android/settingslib/fuelgauge/BatteryStatus.java",
    """    public final int maxChargingWattage;
    public final boolean present;""",
    """    public final int maxChargingWattage;
    public final int maxChargingCurrent;
    public final int maxChargingVoltage;
    public final int temperature;
    public final boolean present;""",
)

replace(
    "frameworks/base/packages/SettingsLib/src/com/android/settingslib/fuelgauge/BatteryStatus.java",
    """        this.maxChargingWattage = maxChargingWattage;
        this.present = present;""",
    """        this.maxChargingWattage = maxChargingWattage;
        this.maxChargingCurrent = -1;
        this.maxChargingVoltage = -1;
        this.temperature = -1;
        this.present = present;""",
)

replace(
    "frameworks/base/packages/SettingsLib/src/com/android/settingslib/fuelgauge/BatteryStatus.java",
    """        maxChargingWattage = calculateMaxChargingMicroWatt(batteryChangedIntent);
    }""",
    """        maxChargingWattage = calculateMaxChargingMicroWatt(batteryChangedIntent);
        maxChargingCurrent = batteryChangedIntent.getIntExtra(EXTRA_MAX_CHARGING_CURRENT, -1);
        maxChargingVoltage = batteryChangedIntent.getIntExtra(EXTRA_MAX_CHARGING_VOLTAGE, -1);
        temperature = batteryChangedIntent.getIntExtra(EXTRA_TEMPERATURE, -1);
    }""",
)

# ---------------------------------------------------------------------------
# frameworks/base: KeyguardIndicationController charging details
# ---------------------------------------------------------------------------
replace(
    "frameworks/base/packages/SystemUI/src/com/android/systemui/statusbar/KeyguardIndicationController.java",
    """import java.io.PrintWriter;
import java.text.NumberFormat;
import java.util.Set;""",
    """import java.io.PrintWriter;
import java.text.NumberFormat;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Set;""",
)

replace(
    "frameworks/base/packages/SystemUI/src/com/android/systemui/statusbar/KeyguardIndicationController.java",
    """    private int mChargingWattage;
    private int mBatteryLevel = -1;""",
    """    private int mChargingWattage;
    private int mChargingCurrent;
    private int mChargingVoltage;
    private int mTemperature;
    private int mCurrentDivider;
    private int mBatteryLevel = -1;""",
)

replace(
    "frameworks/base/packages/SystemUI/src/com/android/systemui/statusbar/KeyguardIndicationController.java",
    """        mContext = context;
        mBroadcastDispatcher = broadcastDispatcher;""",
    """        mContext = context;
        mCurrentDivider = context.getResources().getInteger(R.integer.config_currentInfoDivider);
        mBroadcastDispatcher = broadcastDispatcher;""",
)

replace(
    "frameworks/base/packages/SystemUI/src/com/android/systemui/statusbar/KeyguardIndicationController.java",
    """        if (hasChargingTime) {
            String chargingTimeFormatted = Formatter.formatShortElapsedTimeRoundingUpToMinutes(
                    mContext, mChargingTimeRemaining);
            return mContext.getResources().getString(chargingId, chargingTimeFormatted,
                    percentage);
        } else {
            return mContext.getResources().getString(chargingId, percentage);
        }
    }""",
    """        String chargingDetails = buildChargingDetails();
        if (hasChargingTime) {
            String chargingTimeFormatted = Formatter.formatShortElapsedTimeRoundingUpToMinutes(
                    mContext, mChargingTimeRemaining);
            return mContext.getResources().getString(chargingId, chargingTimeFormatted,
                    percentage) + chargingDetails;
        } else {
            return mContext.getResources().getString(chargingId, percentage) + chargingDetails;
        }
    }

    /**
     * Builds the detailed charging information shown below the charging indication.
     *
     * Based on the lockscreen charging implementation from crDroid, originally by
     * yank555-lu and nathanchance, squashed by maxwen and updated by Pranav Vashi.
     */
    private String buildChargingDetails() {
        // Keep the always-on display indication compact.
        if (mDozing) {
            return "";
        }

        List<String> details = new ArrayList<>();
        if (mChargingCurrent > 0) {
            int currentMa = mChargingCurrent / mCurrentDivider;
            if (currentMa >= 1000) {
                details.add(String.format(Locale.US, "%.1f A", currentMa / 1000f));
            } else {
                details.add(String.format(Locale.US, "%d mA", currentMa));
            }
        }
        if (mChargingWattage > 0) {
            details.add(String.format(Locale.US, "%.1f W", mChargingWattage / 1000000f));
        }
        if (mChargingVoltage > 0) {
            details.add(String.format(Locale.US, "%.1f V", mChargingVoltage / 1000000f));
        }
        if (mTemperature > 0) {
            details.add(String.format(Locale.US, "%.1f°C", mTemperature / 10f));
        }

        return details.isEmpty() ? "" : "\\n" + TextUtils.join(" · ", details);
    }""",
)

replace(
    "frameworks/base/packages/SystemUI/src/com/android/systemui/statusbar/KeyguardIndicationController.java",
    """            mChargingWattage = status.maxChargingWattage;
            mChargingSpeed = status.getChargingSpeed(mContext);""",
    """            mChargingWattage = status.maxChargingWattage;
            mChargingCurrent = status.maxChargingCurrent;
            mChargingVoltage = status.maxChargingVoltage;
            mTemperature = status.temperature;
            mChargingSpeed = status.getChargingSpeed(mContext);""",
)

replace(
    "frameworks/base/packages/SystemUI/src/com/android/systemui/statusbar/KeyguardIndicationController.java",
    """        pw.println("  mChargingWattage: " + mChargingWattage);
        pw.println("  mChargingStatus: " + mChargingStatus);""",
    """        pw.println("  mChargingWattage: " + mChargingWattage);
        pw.println("  mChargingCurrent: " + mChargingCurrent);
        pw.println("  mChargingVoltage: " + mChargingVoltage);
        pw.println("  mTemperature: " + mTemperature);
        pw.println("  mChargingStatus: " + mChargingStatus);""",
)

# ---------------------------------------------------------------------------
# frameworks/base: charging config
# ---------------------------------------------------------------------------
p = ROOT / "frameworks/base/packages/SystemUI/res/values/aospa_config.xml"
text = p.read_text()
if "config_currentInfoDivider" not in text:
    text = text.rsplit("</resources>", 1)[0] + """
    <!-- Divider for charging current details on the lockscreen -->
    <integer name="config_currentInfoDivider" translatable="false">1000</integer>

</resources>
"""
    p.write_text(text)
    print("patched frameworks/base/packages/SystemUI/res/values/aospa_config.xml")

# ---------------------------------------------------------------------------
# frameworks/base: screenshot detection gate
# ---------------------------------------------------------------------------
write(
    "frameworks/base/packages/SystemUI/src/com/android/systemui/screenshot/ScreenshotDetectionController.kt",
    """/*
 * Copyright (C) 2023 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.android.systemui.screenshot

import android.content.Context
import android.content.pm.PackageManager
import android.content.pm.PackageManager.ComponentInfoFlags
import android.content.pm.PackageManager.MATCH_ANY_USER
import android.content.pm.PackageManager.MATCH_DISABLED_COMPONENTS
import android.provider.Settings
import android.view.Display
import android.view.IWindowManager
import android.view.ViewGroup
import android.view.WindowManager
import android.widget.TextView
import com.android.systemui.dagger.qualifiers.Application
import com.android.systemui.res.R
import javax.inject.Inject

class ScreenshotDetectionController
@Inject
constructor(
    @Application private val context: Context,
    private val windowManager: IWindowManager,
    private val packageManager: PackageManager,
) {
    /**
     * Notify potentially listening apps of the screenshot. Return a list of the names of the apps
     * notified.
     */
    fun maybeNotifyOfScreenshot(data: ScreenshotData): List<CharSequence> {
        // No notification for screenshots from overview.
        if (data.source == WindowManager.ScreenshotSource.SCREENSHOT_OVERVIEW) return listOf()

        // The user can disable screenshot detection independently of FLAG_SECURE handling.
        if (Settings.Secure.getInt(
                context.contentResolver,
                Settings.Secure.SCREENSHOT_DETECTION,
                1,
            ) == 0
        ) {
            return listOf()
        }

        // Notify listeners, retrieve a list of listening components.
        val components = windowManager.notifyScreenshotListeners(Display.DEFAULT_DISPLAY)

        // Convert component names to app names.
        return components.map {
            packageManager
                .getActivityInfo(it, ComponentInfoFlags.of(
                    (MATCH_DISABLED_COMPONENTS or MATCH_ANY_USER).toLong()))
                .loadLabel(packageManager)
        }
    }

    fun populateView(view: ViewGroup, appNames: List<CharSequence>) {
        assert(appNames.isNotEmpty())

        val textView: TextView = view.requireViewById(R.id.screenshot_detection_notice_text)
        if (appNames.size == 1) {
            textView.text =
                view.resources.getString(R.string.screenshot_detected_template, appNames[0])
        } else {
            textView.text =
                view.resources.getString(
                    R.string.screenshot_detected_multiple_template,
                    appNames[0]
                )
        }
    }
}
""",
)

replace(
    "frameworks/base/packages/SystemUI/multivalentTests/src/com/android/systemui/screenshot/ScreenshotDetectionControllerTest.kt",
    "        controller = ScreenshotDetectionController(windowManager, packageManager)",
    "        controller = ScreenshotDetectionController(mContext, windowManager, packageManager)",
)

# ---------------------------------------------------------------------------
# frameworks/base: idle radio timeout
# ---------------------------------------------------------------------------
write(
    "frameworks/base/packages/SystemUI/src/com/android/systemui/radio/IdleRadioTimeoutStartable.kt",
    """/*
 * Copyright (C) 2026 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.android.systemui.radio

import android.app.AlarmManager
import android.app.PendingIntent
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothManager
import android.bluetooth.BluetoothProfile
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.database.ContentObserver
import android.net.wifi.SupplicantState
import android.net.wifi.WifiManager
import android.os.Handler
import android.os.Looper
import android.os.SystemClock
import android.provider.Settings
import com.android.systemui.CoreStartable
import com.android.systemui.dagger.SysUISingleton
import com.android.systemui.dagger.qualifiers.Application
import dagger.Binds
import dagger.Module
import dagger.multibindings.ClassKey
import dagger.multibindings.IntoMap
import javax.inject.Inject

/**
 * Turns off Wi-Fi and Bluetooth after five minutes without a connection when the user enables
 * "Turn off Wi-Fi and Bluetooth when idle" in Network & internet.
 */
@SysUISingleton
class IdleRadioTimeoutStartable
@Inject
constructor(
    @Application private val context: Context,
) : CoreStartable {

    private val alarmManager = context.getSystemService(AlarmManager::class.java)
    private val wifiManager = context.getSystemService(WifiManager::class.java)
    private val bluetoothManager = context.getSystemService(BluetoothManager::class.java)
    private val bluetoothAdapter: BluetoothAdapter?
        get() = bluetoothManager?.adapter

    private var wifiTimeoutScheduled = false
    private var bluetoothTimeoutScheduled = false

    private val handler = Handler(Looper.getMainLooper())

    private val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            when (intent.action) {
                ACTION_WIFI_TIMEOUT -> {
                    wifiTimeoutScheduled = false
                    if (isEnabled() && wifiManager?.isWifiEnabled == true && !isWifiConnected()) {
                        wifiManager?.isWifiEnabled = false
                    }
                }
                ACTION_BLUETOOTH_TIMEOUT -> {
                    bluetoothTimeoutScheduled = false
                    if (isEnabled() && bluetoothAdapter?.isEnabled == true &&
                        !isBluetoothConnected()
                    ) {
                        try {
                            bluetoothAdapter?.disable()
                        } catch (e: SecurityException) {
                            // SystemUI is expected to hold BLUETOOTH_CONNECT.
                        }
                    }
                }
            }
            evaluate()
        }
    }

    private val settingsObserver = object : ContentObserver(handler) {
        override fun onChange(selfChange: Boolean) {
            evaluate()
        }
    }

    override fun start() {
        // Clear any alarms left behind by a previous SystemUI process.
        alarmManager?.cancel(pendingIntent(ACTION_WIFI_TIMEOUT, REQUEST_WIFI))
        alarmManager?.cancel(pendingIntent(ACTION_BLUETOOTH_TIMEOUT, REQUEST_BLUETOOTH))

        val filter = IntentFilter().apply {
            addAction(WifiManager.WIFI_STATE_CHANGED_ACTION)
            addAction(WifiManager.NETWORK_STATE_CHANGED_ACTION)
            addAction(BluetoothAdapter.ACTION_STATE_CHANGED)
            addAction(BluetoothAdapter.ACTION_CONNECTION_STATE_CHANGED)
            addAction(BluetoothDevice.ACTION_ACL_CONNECTED)
            addAction(BluetoothDevice.ACTION_ACL_DISCONNECTED)
            addAction(ACTION_WIFI_TIMEOUT)
            addAction(ACTION_BLUETOOTH_TIMEOUT)
        }
        context.registerReceiver(receiver, filter, Context.RECEIVER_NOT_EXPORTED)
        context.contentResolver.registerContentObserver(
            Settings.Secure.getUriFor(Settings.Secure.IDLE_RADIO_TIMEOUT),
            false,
            settingsObserver,
        )
        evaluate()
    }

    private fun evaluate() {
        if (!isEnabled()) {
            cancelWifiTimeout()
            cancelBluetoothTimeout()
            return
        }

        if (wifiManager?.isWifiEnabled == true && !isWifiConnected()) {
            scheduleWifiTimeout()
        } else {
            cancelWifiTimeout()
        }

        if (bluetoothAdapter?.isEnabled == true && !isBluetoothConnected()) {
            scheduleBluetoothTimeout()
        } else {
            cancelBluetoothTimeout()
        }
    }

    private fun isEnabled(): Boolean =
        Settings.Secure.getInt(
            context.contentResolver,
            Settings.Secure.IDLE_RADIO_TIMEOUT,
            0,
        ) == 1

    private fun isWifiConnected(): Boolean {
        val info = wifiManager?.connectionInfo ?: return false
        return info.networkId != WifiManager.INVALID_NETWORK_ID &&
            info.supplicantState == SupplicantState.COMPLETED
    }

    private fun isBluetoothConnected(): Boolean {
        val adapter = bluetoothAdapter ?: return false
        if (!adapter.isEnabled) return false
        return try {
            adapter.connectedDevices.isNotEmpty() ||
                bluetoothManager?.getConnectedDevices(BluetoothProfile.GATT)?.isNotEmpty() == true ||
                bluetoothManager?.getConnectedDevices(
                    BluetoothProfile.GATT_SERVER
                )?.isNotEmpty() == true
        } catch (e: SecurityException) {
            // If the connection state cannot be read, never turn Bluetooth off.
            true
        }
    }

    private fun scheduleWifiTimeout() {
        if (wifiTimeoutScheduled) return
        schedule(ACTION_WIFI_TIMEOUT, REQUEST_WIFI)
        wifiTimeoutScheduled = true
    }

    private fun scheduleBluetoothTimeout() {
        if (bluetoothTimeoutScheduled) return
        schedule(ACTION_BLUETOOTH_TIMEOUT, REQUEST_BLUETOOTH)
        bluetoothTimeoutScheduled = true
    }

    private fun schedule(action: String, requestCode: Int) {
        val pendingIntent = pendingIntent(action, requestCode)
        val triggerAt = SystemClock.elapsedRealtime() + IDLE_TIMEOUT_MS
        try {
            alarmManager?.setExactAndAllowWhileIdle(
                AlarmManager.ELAPSED_REALTIME_WAKEUP,
                triggerAt,
                pendingIntent,
            )
        } catch (e: SecurityException) {
            alarmManager?.setAndAllowWhileIdle(
                AlarmManager.ELAPSED_REALTIME_WAKEUP,
                triggerAt,
                pendingIntent,
            )
        }
    }

    private fun cancelWifiTimeout() {
        if (!wifiTimeoutScheduled) return
        alarmManager?.cancel(pendingIntent(ACTION_WIFI_TIMEOUT, REQUEST_WIFI))
        wifiTimeoutScheduled = false
    }

    private fun cancelBluetoothTimeout() {
        if (!bluetoothTimeoutScheduled) return
        alarmManager?.cancel(pendingIntent(ACTION_BLUETOOTH_TIMEOUT, REQUEST_BLUETOOTH))
        bluetoothTimeoutScheduled = false
    }

    private fun pendingIntent(action: String, requestCode: Int): PendingIntent =
        PendingIntent.getBroadcast(
            context,
            requestCode,
            Intent(action).setPackage(context.packageName),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )

    private companion object {
        const val ACTION_WIFI_TIMEOUT = "com.android.systemui.action.IDLE_WIFI_TIMEOUT"
        const val ACTION_BLUETOOTH_TIMEOUT =
            "com.android.systemui.action.IDLE_BLUETOOTH_TIMEOUT"
        const val REQUEST_WIFI = 1001
        const val REQUEST_BLUETOOTH = 1002
        const val IDLE_TIMEOUT_MS = 5 * 60 * 1000L
    }
}

@Module
interface IdleRadioTimeoutStartableModule {
    @Binds
    @IntoMap
    @ClassKey(IdleRadioTimeoutStartable::class)
    fun startable(startable: IdleRadioTimeoutStartable): CoreStartable
}
""",
)

replace(
    "frameworks/base/packages/SystemUI/src/com/android/systemui/dagger/SystemUIModule.java",
    "import com.android.systemui.classifier.FalsingModule;",
    """import com.android.systemui.classifier.FalsingModule;
import com.android.systemui.radio.IdleRadioTimeoutStartableModule;""",
)

replace(
    "frameworks/base/packages/SystemUI/src/com/android/systemui/dagger/SystemUIModule.java",
    """        FalsingModule.class,
        FlagsModule.class,""",
    """        FalsingModule.class,
        IdleRadioTimeoutStartableModule.class,
        FlagsModule.class,""",
)

# ---------------------------------------------------------------------------
# packages/apps/Settings: display + network toggles
# ---------------------------------------------------------------------------
replace(
    "packages/apps/Settings/res/xml/display_settings.xml",
    """        <!-- Status bar burn-in protection -->
        <co.aospa.framework.preference.SecureSettingSwitchPreference
            android:key="status_bar_burn_in_protection"
            android:title="@string/status_bar_burn_in_protection_title"
            android:summary="@string/status_bar_burn_in_protection_summary"
            android:defaultValue="true" />
    </PreferenceCategory>""",
    """        <!-- Status bar burn-in protection -->
        <co.aospa.framework.preference.SecureSettingSwitchPreference
            android:key="status_bar_burn_in_protection"
            android:title="@string/status_bar_burn_in_protection_title"
            android:summary="@string/status_bar_burn_in_protection_summary"
            android:defaultValue="true" />

        <!-- Window ignore secure, based on LibXZR's feature -->
        <co.aospa.framework.preference.SecureSettingSwitchPreference
            android:key="window_ignore_secure"
            android:title="@string/ignore_window_secure_title"
            android:summary="@string/ignore_window_secure_summary"
            android:defaultValue="false" />

        <!-- Screenshot detection -->
        <co.aospa.framework.preference.SecureSettingSwitchPreference
            android:key="screenshot_detection"
            android:title="@string/screenshot_detection_title"
            android:summary="@string/screenshot_detection_summary"
            android:defaultValue="true" />
    </PreferenceCategory>""",
)

replace(
    "packages/apps/Settings/res/xml/network_provider_internet.xml",
    """    <com.android.settingslib.RestrictedSwitchPreference
        android:key="airplane_mode_on"
        android:title="@string/airplane_mode"
        android:icon="@drawable/ic_airplanemode_active"
        android:order="-5"
        settings:controller="com.android.settings.network.AirplaneModePreferenceController"
        settings:userRestriction="no_airplane_mode"/>""",
    """    <com.android.settingslib.RestrictedSwitchPreference
        android:key="airplane_mode_on"
        android:title="@string/airplane_mode"
        android:icon="@drawable/ic_airplanemode_active"
        android:order="-5"
        settings:controller="com.android.settings.network.AirplaneModePreferenceController"
        settings:userRestriction="no_airplane_mode"/>

    <co.aospa.framework.preference.SecureSettingSwitchPreference
        android:key="idle_radio_timeout"
        android:title="@string/idle_radio_timeout_title"
        android:summary="@string/idle_radio_timeout_summary"
        android:order="0"
        android:defaultValue="false"/>""",
)

p = ROOT / "packages/apps/Settings/res/values/aospa_strings.xml"
text = p.read_text()
if "idle_radio_timeout_title" not in text:
    text = text.rsplit("</resources>", 1)[0] + """
    <!-- Screenshot detection -->
    <string name="screenshot_detection_title">Screenshot detection</string>
    <string name="screenshot_detection_summary">Allow apps to know when you take a screenshot. Turn off to prevent apps from detecting screenshots.</string>

    <!-- Idle radio timeout -->
    <string name="idle_radio_timeout_title">Turn off Wi-Fi and Bluetooth when idle</string>
    <string name="idle_radio_timeout_summary">Automatically turn off Wi-Fi and Bluetooth after 5 minutes without a connection</string>

</resources>
"""
    p.write_text(text)
    print("patched packages/apps/Settings/res/values/aospa_strings.xml")

# ---------------------------------------------------------------------------
# vendor/aospa: enable AOSP scene container + dual shade
# ---------------------------------------------------------------------------
write(
    "vendor/aospa/release/aconfig/cp2a/com.android.systemui/scene_container_flag_values.textproto",
    """flag_value {
  package: "com.android.systemui"
  name: "scene_container"
  state: ENABLED
  permission: READ_ONLY
}
""",
)

write(
    "vendor/aospa/release/aconfig/cp2a/com.android.systemui/dual_shade_flag_values.textproto",
    """flag_value {
  package: "com.android.systemui"
  name: "dual_shade"
  state: ENABLED
  permission: READ_ONLY
}
""",
)

print("done")
