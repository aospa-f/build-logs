from pathlib import Path

base = Path("/serverhive5/raizenftw/aospa")

def rep(path, old, new):
    p = base / path
    t = p.read_text()
    assert t.count(old) == 1, (path, t.count(old))
    p.write_text(t.replace(old, new, 1))
    print("patched", path)

rep(
    "device/oneplus/giulia/overlay/OPlusFrameworksResTarget/res/values/config.xml",
    "    <string-array name=\"config_deviceKeyHandlerClasses\" translatable=\"false\">\n"
    "        <item>org.lineageos.settings.device.KeyHandler</item>\n"
    "    </string-array>\n"
    "</resources>\n",
    "    <string-array name=\"config_deviceKeyHandlerClasses\" translatable=\"false\">\n"
    "        <item>org.lineageos.settings.device.KeyHandler</item>\n"
    "    </string-array>\n"
    "\n"
    "    <!-- Screen off touch gestures. Key codes come from the OPlus/Synaptics touch HAL:\n"
    "         246 + gesture id. -->\n"
    "    <bool name=\"config_enableKeyHandler\">true</bool>\n"
    "    <integer name=\"config_drawArrowLeftKeyCode\">250</integer>\n"
    "    <integer name=\"config_drawArrowRightKeyCode\">251</integer>\n"
    "    <integer name=\"config_drawOKeyCode\">252</integer>\n"
    "    <integer name=\"config_oneFingerSwipeUpKeyCode\">257</integer>\n"
    "    <integer name=\"config_oneFingerSwipeDownKeyCode\">256</integer>\n"
    "\n"
    "    <!-- Default actions: previous, next, play/pause, volume up, volume down -->\n"
    "    <integer name=\"config_drawArrowLeftDefault\">7</integer>\n"
    "    <integer name=\"config_drawArrowRightDefault\">6</integer>\n"
    "    <integer name=\"config_drawODefault\">5</integer>\n"
    "    <integer name=\"config_oneFingerSwipeUpDefault\">10</integer>\n"
    "    <integer name=\"config_oneFingerSwipeDownDefault\">11</integer>\n"
    "</resources>\n",
)

rep(
    "device/oneplus/sm8650-common/init/init.oplus.rc",
    "on boot\n"
    "    # Display\n"
    "    chmod 0000 /sys/kernel/oplus_display/hbm\n",
    "on boot\n"
    "    # Display\n"
    "    chmod 0000 /sys/kernel/oplus_display/hbm\n"
    "\n"
    "    # Enable screen off touch gestures: left/right Vee, circle, one-finger up/down.\n"
    "    # Bit mask uses gesture IDs from the touch HAL (246 + id).\n"
    "    write /proc/touchpanel/double_tap_enable_indep 3184\n",
)
