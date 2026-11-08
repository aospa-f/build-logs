from pathlib import Path

base = Path("/serverhive5/raizenftw/aospa")
p = base / "frameworks/base/services/core/java/com/android/server/policy/KeyHandler.java"

def rep(old, new):
    t = p.read_text()
    assert t.count(old) == 1, ("KeyHandler", t.count(old))
    p.write_text(t.replace(old, new, 1))
    print("patched KeyHandler")

rep(
    "import android.media.AudioManager;\n"
    "import android.media.session.MediaSessionLegacyHelper;\n",
    "import android.media.AudioManager;\n"
    "import android.media.session.MediaController;\n"
    "import android.media.session.MediaSessionLegacyHelper;\n"
    "import android.media.session.MediaSessionManager;\n"
    "import android.media.session.PlaybackState;\n",
)

rep(
    "import java.lang.IllegalArgumentException;\n",
    "import java.lang.IllegalArgumentException;\n"
    "import java.util.HashSet;\n"
    "import java.util.Set;\n",
)

rep(
    "    private static final int CAMERA = 8;\n"
    "    private static final int DIALER = 9;\n",
    "    private static final int CAMERA = 8;\n"
    "    private static final int DIALER = 9;\n"
    "    private static final int VOLUME_UP = 10;\n"
    "    private static final int VOLUME_DOWN = 11;\n"
    "\n"
    "    private static final String SETTING_OFFSCREEN_MUSIC_APPS =\n"
    "            \"offscreen_gesture_music_apps\";\n",
)

rep(
    "            case MUSIC_PLAY_PAUSE:\n"
    "                handled = dispatchMediaKeyWithWakeLockToMediaSession(KeyEvent.KEYCODE_MEDIA_PLAY_PAUSE);\n"
    "                vibrate = true;\n"
    "                break;\n",
    "            case MUSIC_PLAY_PAUSE:\n"
    "                handled = isMusicActiveForGesture()\n"
    "                        && dispatchMediaKeyWithWakeLockToMediaSession(\n"
    "                                KeyEvent.KEYCODE_MEDIA_PLAY_PAUSE);\n"
    "                vibrate = true;\n"
    "                break;\n",
)

rep(
    "            case MUSIC_PREVIOUS:\n"
    "                handled = isMusicActive() && dispatchMediaKeyWithWakeLockToMediaSession(KeyEvent.KEYCODE_MEDIA_PREVIOUS);\n"
    "                vibrate = true;\n"
    "                break;\n"
    "            case MUSIC_NEXT:\n"
    "                handled = isMusicActive() && dispatchMediaKeyWithWakeLockToMediaSession(KeyEvent.KEYCODE_MEDIA_NEXT);\n"
    "                vibrate = true;\n"
    "                break;\n",
    "            case MUSIC_PREVIOUS:\n"
    "                handled = isMusicActiveForGesture()\n"
    "                        && dispatchMediaKeyWithWakeLockToMediaSession(\n"
    "                                KeyEvent.KEYCODE_MEDIA_PREVIOUS);\n"
    "                vibrate = true;\n"
    "                break;\n"
    "            case MUSIC_NEXT:\n"
    "                handled = isMusicActiveForGesture()\n"
    "                        && dispatchMediaKeyWithWakeLockToMediaSession(\n"
    "                                KeyEvent.KEYCODE_MEDIA_NEXT);\n"
    "                vibrate = true;\n"
    "                break;\n"
    "            case VOLUME_UP:\n"
    "                handled = isMusicActiveForGesture()\n"
    "                        && adjustMusicVolume(AudioManager.ADJUST_RAISE);\n"
    "                vibrate = true;\n"
    "                break;\n"
    "            case VOLUME_DOWN:\n"
    "                handled = isMusicActiveForGesture()\n"
    "                        && adjustMusicVolume(AudioManager.ADJUST_LOWER);\n"
    "                vibrate = true;\n"
    "                break;\n",
)

rep(
    "    private boolean isMusicActive() {\n"
    "        if (mAudioManager != null) {\n"
    "            return mAudioManager.isMusicActive();\n"
    "        }\n"
    "        return false;\n"
    "    }\n",
    "    private boolean isMusicActive() {\n"
    "        if (mAudioManager != null) {\n"
    "            return mAudioManager.isMusicActive();\n"
    "        }\n"
    "        return false;\n"
    "    }\n"
    "\n"
    "    private boolean isMusicActiveForGesture() {\n"
    "        if (!isMusicActive()) {\n"
    "            return false;\n"
    "        }\n"
    "\n"
    "        final String allowed = Settings.System.getStringForUser(\n"
    "                mContext.getContentResolver(), SETTING_OFFSCREEN_MUSIC_APPS,\n"
    "                UserHandle.USER_CURRENT);\n"
    "        if (TextUtils.isEmpty(allowed)) {\n"
    "            return true;\n"
    "        }\n"
    "\n"
    "        final Set<String> allowedPackages = new HashSet<>();\n"
    "        for (String pkg : allowed.split(\",\")) {\n"
    "            if (!TextUtils.isEmpty(pkg)) {\n"
    "                allowedPackages.add(pkg);\n"
    "            }\n"
    "        }\n"
    "        if (allowedPackages.isEmpty()) {\n"
    "            return true;\n"
    "        }\n"
    "\n"
    "        final MediaSessionManager manager =\n"
    "                mContext.getSystemService(MediaSessionManager.class);\n"
    "        if (manager == null) {\n"
    "            return false;\n"
    "        }\n"
    "        try {\n"
    "            for (MediaController controller : manager.getActiveSessions(null)) {\n"
    "                final PlaybackState state = controller.getPlaybackState();\n"
    "                if (state != null && state.getState() == PlaybackState.STATE_PLAYING\n"
    "                        && allowedPackages.contains(controller.getPackageName())) {\n"
    "                    return true;\n"
    "                }\n"
    "            }\n"
    "        } catch (Exception e) {\n"
    "            Log.w(TAG, \"Unable to query active media sessions\", e);\n"
    "        }\n"
    "        return false;\n"
    "    }\n"
    "\n"
    "    private boolean adjustMusicVolume(int direction) {\n"
    "        if (mAudioManager == null) {\n"
    "            return false;\n"
    "        }\n"
    "        mAudioManager.adjustStreamVolume(AudioManager.STREAM_MUSIC, direction, 0);\n"
    "        return true;\n"
    "    }\n",
)
