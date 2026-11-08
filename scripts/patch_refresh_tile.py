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
    "frameworks/base/packages/SystemUI/src/com/android/systemui/qs/tiles/RefreshRateTile.kt",
    '''/*
 * Copyright (C) 2026 The AOSPA Project
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

package com.android.systemui.qs.tiles

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.database.ContentObserver
import android.hardware.display.DisplayManager
import android.os.Handler
import android.os.Looper
import android.os.PowerManager
import android.provider.Settings
import android.service.quicksettings.Tile
import android.view.Display

import com.android.internal.logging.MetricsLogger
import com.android.internal.logging.nano.MetricsProto.MetricsEvent
import com.android.systemui.animation.Expandable
import com.android.systemui.dagger.qualifiers.Background
import com.android.systemui.dagger.qualifiers.Main
import com.android.systemui.plugins.ActivityStarter
import com.android.systemui.plugins.FalsingManager
import com.android.systemui.plugins.qs.QSTile
import com.android.systemui.plugins.statusbar.StatusBarStateController
import com.android.systemui.qs.QSHost
import com.android.systemui.qs.QsEventLogger
import com.android.systemui.qs.logging.QSLogger
import com.android.systemui.qs.tileimpl.QSTileImpl
import com.android.systemui.res.R

import javax.inject.Inject
import kotlin.math.roundToInt

/** Two-mode refresh-rate tile: 90 Hz adaptive and 120 Hz locked. */
class RefreshRateTile
@Inject
constructor(
    host: QSHost,
    uiEventLogger: QsEventLogger,
    @Background backgroundLooper: Looper,
    @Main mainHandler: Handler,
    falsingManager: FalsingManager,
    metricsLogger: MetricsLogger,
    statusBarStateController: StatusBarStateController,
    activityStarter: ActivityStarter,
    qsLogger: QSLogger,
) : QSTileImpl<QSTile.State>(
    host,
    uiEventLogger,
    backgroundLooper,
    mainHandler,
    falsingManager,
    metricsLogger,
    statusBarStateController,
    activityStarter,
    qsLogger,
) {

    private val powerManager = mContext.getSystemService(PowerManager::class.java)
    private val displayManager = mContext.getSystemService(DisplayManager::class.java)

    private var listening = false

    private val observer = object : ContentObserver(mainHandler) {
        override fun onChange(selfChange: Boolean) {
            refreshState()
        }
    }

    private val powerSaveReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            refreshState()
        }
    }

    override fun isAvailable(): Boolean {
        val display = displayManager?.getDisplay(Display.DEFAULT_DISPLAY) ?: return false
        val rates = display.supportedModes.map { it.refreshRate.roundToInt() }.toSet()
        return rates.contains(ADAPTIVE_RATE) && rates.contains(LOCKED_RATE)
    }

    override fun newTileState(): QSTile.State = QSTile.State()

    override fun handleSetListening(listening: Boolean) {
        super.handleSetListening(listening)
        if (listening == this.listening) {
            return
        }
        this.listening = listening
        if (listening) {
            val resolver = mContext.contentResolver
            resolver.registerContentObserver(
                Settings.System.getUriFor(Settings.System.MIN_REFRESH_RATE),
                false,
                observer,
            )
            resolver.registerContentObserver(
                Settings.System.getUriFor(Settings.System.PEAK_REFRESH_RATE),
                false,
                observer,
            )
            mContext.registerReceiver(
                powerSaveReceiver,
                IntentFilter(PowerManager.ACTION_POWER_SAVE_MODE_CHANGED),
                Context.RECEIVER_NOT_EXPORTED,
            )
        } else {
            mContext.contentResolver.unregisterContentObserver(observer)
            mContext.unregisterReceiver(powerSaveReceiver)
        }
    }

    override fun handleClick(expandable: Expandable?) {
        setLocked(!isLocked())
    }

    override fun handleUpdateState(state: QSTile.State, arg: Any?) {
        val locked = isLocked()
        val powerSave = powerManager?.isPowerSaveMode == true
        state.state = if (powerSave) Tile.STATE_UNAVAILABLE else Tile.STATE_ACTIVE
        state.label = getTileLabel()
        state.secondaryLabel = when {
            powerSave -> mContext.getString(R.string.refresh_rate_tile_battery_saver)
            locked -> mContext.getString(R.string.refresh_rate_tile_120)
            else -> mContext.getString(R.string.refresh_rate_tile_90_adaptive)
        }
        state.contentDescription = state.label
        state.icon = ResourceIcon.get(R.drawable.ic_refresh_rate)
    }

    override fun getLongClickIntent(): Intent =
        Intent("android.settings.REFRESH_RATE_SETTINGS")

    override fun getTileLabel(): CharSequence =
        mContext.getString(R.string.refresh_rate_tile_label)

    override fun getMetricsCategory(): Int = MetricsEvent.DISPLAY

    private fun isLocked(): Boolean {
        val resolver = mContext.contentResolver
        val min = Settings.System.getFloat(
            resolver,
            Settings.System.MIN_REFRESH_RATE,
            0f,
        )
        val peak = Settings.System.getFloat(
            resolver,
            Settings.System.PEAK_REFRESH_RATE,
            LOCKED_RATE.toFloat(),
        )
        return min >= LOCKED_RATE && peak >= LOCKED_RATE
    }

    private fun setLocked(locked: Boolean) {
        val resolver = mContext.contentResolver
        if (locked) {
            Settings.System.putFloat(resolver, Settings.System.PEAK_REFRESH_RATE, LOCKED_RATE.toFloat())
            Settings.System.putFloat(resolver, Settings.System.MIN_REFRESH_RATE, LOCKED_RATE.toFloat())
        } else {
            Settings.System.putFloat(resolver, Settings.System.PEAK_REFRESH_RATE, ADAPTIVE_RATE.toFloat())
            Settings.System.putFloat(resolver, Settings.System.MIN_REFRESH_RATE, 0f)
        }
        refreshState()
    }

    companion object {
        const val TILE_SPEC = "refresh_rate"
        private const val ADAPTIVE_RATE = 90
        private const val LOCKED_RATE = 120
    }
}
''',
)

write(
    "frameworks/base/packages/SystemUI/src/com/android/systemui/qs/tiles/RefreshRateTileModule.kt",
    '''/*
 * Copyright (C) 2026 The AOSPA Project
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

package com.android.systemui.qs.tiles

import com.android.systemui.qs.tileimpl.QSTileImpl
import dagger.Binds
import dagger.Module
import dagger.multibindings.IntoMap
import dagger.multibindings.StringKey

@Module
interface RefreshRateTileModule {

    @Binds
    @IntoMap
    @StringKey(RefreshRateTile.TILE_SPEC)
    fun bindRefreshRateTile(tile: RefreshRateTile): QSTileImpl<*>
}
''',
)

write(
    "frameworks/base/packages/SystemUI/res/drawable/ic_refresh_rate.xml",
    '''<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24"
    android:tint="?attr/colorControlNormal">
    <path
        android:fillColor="@android:color/white"
        android:pathData="M17.65,6.35C16.2,4.9 14.21,4 12,4c-4.42,0 -7.99,3.58 -7.99,8s3.57,8 7.99,8c3.73,0 6.84,-2.55 7.73,-6h-2.08c-0.82,2.33 -3.04,4 -5.65,4 -3.31,0 -6,-2.69 -6,-6s2.69,-6 6,-6c1.66,0 3.14,0.69 4.22,1.78L13,11h7V4l-2.35,2.35z" />
</vector>
''',
)

rep(
    "frameworks/base/packages/SystemUI/res/values/config.xml",
    "internet,wifi,bt,flashlight,dnd,modes_dnd,alarm,airplane,controls,wallet,rotation,battery,cast,screenrecord,mictoggle,cameratoggle,location,hotspot,inversion,saver,dark,work,night,reverse,reduce_brightness,qr_code_scanner,onehanded,color_correction,font_scaling,record_issue,hearing_devices,notes,desktopeffects,cell\n",
    "internet,wifi,bt,flashlight,dnd,modes_dnd,alarm,airplane,controls,wallet,rotation,battery,cast,screenrecord,mictoggle,cameratoggle,location,hotspot,inversion,saver,dark,work,night,reverse,reduce_brightness,qr_code_scanner,onehanded,color_correction,font_scaling,record_issue,hearing_devices,notes,desktopeffects,cell,refresh_rate\n",
)

rep(
    "frameworks/base/packages/SystemUI/res/values/aospa_strings.xml",
    "</resources>\n",
    '''
    <!-- Refresh rate tile -->
    <string name="refresh_rate_tile_label">Refresh rate</string>
    <string name="refresh_rate_tile_90_adaptive">90 Hz adaptive</string>
    <string name="refresh_rate_tile_120">120 Hz</string>
    <string name="refresh_rate_tile_battery_saver">Battery saver enabled</string>
</resources>
''',
)

rep(
    "frameworks/base/packages/SystemUI/src/com/android/systemui/dagger/SystemUIModule.java",
    "import com.android.systemui.qs.tiles.NotesTile;\n",
    "import com.android.systemui.qs.tiles.NotesTile;\nimport com.android.systemui.qs.tiles.RefreshRateTileModule;\n",
)

rep(
    "frameworks/base/packages/SystemUI/src/com/android/systemui/dagger/SystemUIModule.java",
    "        ScreenRecordModule.class,\n",
    "        ScreenRecordModule.class,\n        RefreshRateTileModule.class,\n",
)
