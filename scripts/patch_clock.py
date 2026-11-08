from pathlib import Path

base = Path("/serverhive5/raizenftw/aospa")

def rep(path, old, new):
    p = base / path
    t = p.read_text()
    assert t.count(old) == 1, (path, t.count(old))
    p.write_text(t.replace(old, new, 1))
    print("patched", path)

# TunerService.parseInteger
rep(
    "frameworks/base/packages/SystemUI/src/com/android/systemui/tuner/TunerService.java",
    "    public static boolean parseIntegerSwitch(String value, boolean defaultValue) {\n"
    "        try {\n"
    "            return value != null ? Integer.parseInt(value) != 0 : defaultValue;\n"
    "        } catch (NumberFormatException e) {\n"
    "            return defaultValue;\n"
    "        }\n"
    "    }\n",
    "    public static boolean parseIntegerSwitch(String value, boolean defaultValue) {\n"
    "        try {\n"
    "            return value != null ? Integer.parseInt(value) != 0 : defaultValue;\n"
    "        } catch (NumberFormatException e) {\n"
    "            return defaultValue;\n"
    "        }\n"
    "    }\n\n"
    "    public static int parseInteger(String value, int defaultValue) {\n"
    "        try {\n"
    "            return value != null ? Integer.parseInt(value) : defaultValue;\n"
    "        } catch (NumberFormatException e) {\n"
    "            return defaultValue;\n"
    "        }\n"
    "    }\n",
)

# Clock imports
rep(
    "frameworks/base/packages/SystemUI/src/com/android/systemui/statusbar/policy/Clock.java",
    "import android.content.res.TypedArray;\n"
    "import android.graphics.Rect;\n",
    "import android.content.res.TypedArray;\n"
    "import android.graphics.Rect;\n"
    "import android.graphics.Typeface;\n",
)
rep(
    "frameworks/base/packages/SystemUI/src/com/android/systemui/statusbar/policy/Clock.java",
    "import java.util.ArrayList;\n"
    "import java.util.Calendar;\n"
    "import java.util.Locale;\n",
    "import java.util.ArrayList;\n"
    "import java.util.Calendar;\n"
    "import java.util.Date;\n"
    "import java.util.Locale;\n",
)

# Clock constants and fields
rep(
    "frameworks/base/packages/SystemUI/src/com/android/systemui/statusbar/policy/Clock.java",
    "    public static final String CLOCK_SECONDS = \"clock_seconds\";\n"
    "    private static final String CLOCK_SUPER_PARCELABLE = \"clock_super_parcelable\";\n",
    "    public static final String CLOCK_SECONDS = \"clock_seconds\";\n"
    "    public static final String STATUS_BAR_CLOCK_AM_PM = \"status_bar_clock_am_pm\";\n"
    "    public static final String STATUS_BAR_CLOCK_DATE_DISPLAY = \"status_bar_clock_date_display\";\n"
    "    public static final String STATUS_BAR_CLOCK_DATE_STYLE = \"status_bar_clock_date_style\";\n"
    "    public static final String STATUS_BAR_CLOCK_DATE_POSITION = \"status_bar_clock_date_position\";\n"
    "    public static final String STATUS_BAR_CLOCK_DATE_FORMAT = \"status_bar_clock_date_format\";\n"
    "    public static final String STATUS_BAR_CLOCK_PERIOD_SEPARATOR =\n"
    "            \"status_bar_clock_period_separator\";\n"
    "    public static final String STATUS_BAR_CLOCK_BOLD = \"status_bar_clock_bold\";\n"
    "    private static final String CLOCK_SUPER_PARCELABLE = \"clock_super_parcelable\";\n",
)
rep(
    "frameworks/base/packages/SystemUI/src/com/android/systemui/statusbar/policy/Clock.java",
    "    private static final int AM_PM_STYLE_NORMAL  = 0;\n"
    "    private static final int AM_PM_STYLE_SMALL   = 1;\n"
    "    private static final int AM_PM_STYLE_GONE    = 2;\n"
    "\n"
    "    private final int mAmPmStyle;\n"
    "    private boolean mShowSeconds;\n"
    "    private Handler mSecondsHandler;\n",
    "    private static final int AM_PM_STYLE_NORMAL  = 0;\n"
    "    private static final int AM_PM_STYLE_SMALL   = 1;\n"
    "    private static final int AM_PM_STYLE_GONE    = 2;\n"
    "\n"
    "    private static final int CLOCK_DATE_DISPLAY_GONE = 0;\n"
    "    private static final int CLOCK_DATE_DISPLAY_SMALL = 1;\n"
    "    private static final int CLOCK_DATE_DISPLAY_NORMAL = 2;\n"
    "\n"
    "    private static final int CLOCK_DATE_STYLE_REGULAR = 0;\n"
    "    private static final int CLOCK_DATE_STYLE_LOWERCASE = 1;\n"
    "    private static final int CLOCK_DATE_STYLE_UPPERCASE = 2;\n"
    "\n"
    "    private static final int STYLE_DATE_LEFT = 0;\n"
    "    private static final int STYLE_DATE_RIGHT = 1;\n"
    "\n"
    "    private int mDefaultAmPmStyle;\n"
    "    private int mAmPmStyle;\n"
    "    private boolean mShowSeconds;\n"
    "    private Handler mSecondsHandler;\n"
    "    private int mClockDateDisplay = CLOCK_DATE_DISPLAY_GONE;\n"
    "    private int mClockDateStyle = CLOCK_DATE_STYLE_REGULAR;\n"
    "    private int mClockDatePosition = STYLE_DATE_LEFT;\n"
    "    private String mClockDateFormat;\n"
    "    private boolean mPeriodHourMinuteSeparator;\n"
    "    private boolean mBoldStatusBarClock;\n"
    "    private boolean mIsStatusBar;\n",
)

# Constructor
rep(
    "frameworks/base/packages/SystemUI/src/com/android/systemui/statusbar/policy/Clock.java",
    "        try {\n"
    "            mAmPmStyle = a.getInt(R.styleable.Clock_amPmStyle, AM_PM_STYLE_GONE);\n"
    "            mNonAdaptedColor = getCurrentTextColor();\n"
    "        } finally {\n",
    "        try {\n"
    "            mDefaultAmPmStyle = a.getInt(R.styleable.Clock_amPmStyle, AM_PM_STYLE_GONE);\n"
    "            mAmPmStyle = mDefaultAmPmStyle;\n"
    "            mIsStatusBar = a.getBoolean(R.styleable.Clock_isStatusBar, false);\n"
    "            mNonAdaptedColor = getCurrentTextColor();\n"
    "        } finally {\n",
)

# Attach tunables
rep(
    "frameworks/base/packages/SystemUI/src/com/android/systemui/statusbar/policy/Clock.java",
    "            Dependency.get(TunerService.class).addTunable(this, CLOCK_SECONDS,\n"
    "                    StatusBarIconController.ICON_HIDE_LIST);\n",
    "            Dependency.get(TunerService.class).addTunable(this, CLOCK_SECONDS,\n"
    "                    StatusBarIconController.ICON_HIDE_LIST,\n"
    "                    STATUS_BAR_CLOCK_AM_PM,\n"
    "                    STATUS_BAR_CLOCK_DATE_DISPLAY,\n"
    "                    STATUS_BAR_CLOCK_DATE_STYLE,\n"
    "                    STATUS_BAR_CLOCK_DATE_POSITION,\n"
    "                    STATUS_BAR_CLOCK_DATE_FORMAT,\n"
    "                    STATUS_BAR_CLOCK_PERIOD_SEPARATOR,\n"
    "                    STATUS_BAR_CLOCK_BOLD);\n",
)
rep(
    "frameworks/base/packages/SystemUI/src/com/android/systemui/statusbar/policy/Clock.java",
    "        // Make sure we update to the current time\n"
    "        updateClock();\n"
    "        updateShowSeconds();\n"
    "    }\n",
    "        // Make sure we update to the current time\n"
    "        updateClock();\n"
    "        updateShowSeconds();\n"
    "        applyBoldClockStyle();\n"
    "    }\n",
)

# updateClock
rep(
    "frameworks/base/packages/SystemUI/src/com/android/systemui/statusbar/policy/Clock.java",
    "    final void updateClock() {\n"
    "        if (mDemoMode) return;\n"
    "        mCalendar.setTimeInMillis(System.currentTimeMillis());\n"
    "        CharSequence smallTime = getSmallTime();\n"
    "        // Setting text actually triggers a layout pass (because the text view is set to\n"
    "        // wrap_content width and TextView always relayouts for this). Avoid needless\n"
    "        // relayout if the text didn't actually change.\n"
    "        if (!TextUtils.equals(smallTime, getText())) {\n"
    "            setText(smallTime);\n"
    "        }\n"
    "        setContentDescription(mContentDescriptionFormat.format(mCalendar.getTime()));\n"
    "    }\n",
    "    final void updateClock() {\n"
    "        updateClock(false);\n"
    "    }\n"
    "\n"
    "    final void updateClock(boolean forceTextUpdate) {\n"
    "        if (mDemoMode || mCalendar == null) return;\n"
    "        mCalendar.setTimeInMillis(System.currentTimeMillis());\n"
    "        CharSequence smallTime = getSmallTime();\n"
    "        // Setting text actually triggers a layout pass (because the text view is set to\n"
    "        // wrap_content width and TextView always relayouts for this). Avoid needless\n"
    "        // relayout if the text didn't actually change.\n"
    "        if (forceTextUpdate || !TextUtils.equals(smallTime, getText())) {\n"
    "            setText(smallTime);\n"
    "        }\n"
    "        if (mContentDescriptionFormat != null) {\n"
    "            setContentDescription(mContentDescriptionFormat.format(mCalendar.getTime()));\n"
    "        }\n"
    "    }\n",
)

# onTuningChanged
rep(
    "frameworks/base/packages/SystemUI/src/com/android/systemui/statusbar/policy/Clock.java",
    "    @Override\n"
    "    public void onTuningChanged(String key, String newValue) {\n"
    "        if (CLOCK_SECONDS.equals(key)) {\n"
    "            mShowSeconds = TunerService.parseIntegerSwitch(newValue, false);\n"
    "            updateShowSeconds();\n"
    "        }\n"
    "    }\n",
    "    @Override\n"
    "    public void onTuningChanged(String key, String newValue) {\n"
    "        switch (key) {\n"
    "            case CLOCK_SECONDS:\n"
    "                mShowSeconds = TunerService.parseIntegerSwitch(newValue, false);\n"
    "                updateShowSeconds();\n"
    "                break;\n"
    "            case STATUS_BAR_CLOCK_AM_PM:\n"
    "                if (mIsStatusBar) {\n"
    "                    mAmPmStyle = TunerService.parseInteger(newValue, mDefaultAmPmStyle);\n"
    "                }\n"
    "                break;\n"
    "            case STATUS_BAR_CLOCK_DATE_DISPLAY:\n"
    "                if (mIsStatusBar) {\n"
    "                    mClockDateDisplay = TunerService.parseInteger(newValue,\n"
    "                            CLOCK_DATE_DISPLAY_GONE);\n"
    "                }\n"
    "                break;\n"
    "            case STATUS_BAR_CLOCK_DATE_STYLE:\n"
    "                if (mIsStatusBar) {\n"
    "                    mClockDateStyle = TunerService.parseInteger(newValue,\n"
    "                            CLOCK_DATE_STYLE_REGULAR);\n"
    "                }\n"
    "                break;\n"
    "            case STATUS_BAR_CLOCK_DATE_POSITION:\n"
    "                if (mIsStatusBar) {\n"
    "                    mClockDatePosition = TunerService.parseInteger(newValue, STYLE_DATE_LEFT);\n"
    "                }\n"
    "                break;\n"
    "            case STATUS_BAR_CLOCK_DATE_FORMAT:\n"
    "                if (mIsStatusBar) {\n"
    "                    mClockDateFormat = newValue;\n"
    "                }\n"
    "                break;\n"
    "            case STATUS_BAR_CLOCK_PERIOD_SEPARATOR:\n"
    "                if (mIsStatusBar) {\n"
    "                    mPeriodHourMinuteSeparator =\n"
    "                            TunerService.parseIntegerSwitch(newValue, false);\n"
    "                }\n"
    "                break;\n"
    "            case STATUS_BAR_CLOCK_BOLD:\n"
    "                if (mIsStatusBar) {\n"
    "                    mBoldStatusBarClock =\n"
    "                            TunerService.parseIntegerSwitch(newValue, false);\n"
    "                    applyBoldClockStyle();\n"
    "                }\n"
    "                break;\n"
    "            default:\n"
    "                break;\n"
    "        }\n"
    "        mContentDescriptionFormatString = \"\";\n"
    "        mDateTimePatternGenerator = null;\n"
    "        updateClock(true);\n"
    "    }\n",
)

# getSmallTime tail
old_tail = '''        String result = mClockFormat.format(mCalendar.getTime());

        if (mAmPmStyle != AM_PM_STYLE_NORMAL) {
            int magic1 = result.indexOf(MAGIC1);
            int magic2 = result.indexOf(MAGIC2);
            if (magic1 >= 0 && magic2 > magic1) {
                SpannableStringBuilder formatted = new SpannableStringBuilder(result);
                if (mAmPmStyle == AM_PM_STYLE_GONE) {
                    formatted.delete(magic1, magic2 + 1);
                } else {
                    if (mAmPmStyle == AM_PM_STYLE_SMALL) {
                        CharacterStyle style = new RelativeSizeSpan(0.7f);
                        formatted.setSpan(style, magic1, magic2,
                                Spannable.SPAN_EXCLUSIVE_INCLUSIVE);
                    }
                    formatted.delete(magic2, magic2 + 1);
                    formatted.delete(magic1, magic1 + 1);
                }
                return formatted;
            }
        }

        return result;

    }
'''
new_tail = '''        String timeResult = mClockFormat.format(mCalendar.getTime());
        if (mIsStatusBar && mPeriodHourMinuteSeparator) {
            timeResult = timeResult.replace(':', '.').replace('\\uFF1A', '.');
        }

        SpannableStringBuilder timeFormatted = new SpannableStringBuilder(timeResult);
        if (mAmPmStyle != AM_PM_STYLE_NORMAL) {
            int magic1 = timeResult.indexOf(MAGIC1);
            int magic2 = timeResult.indexOf(MAGIC2);
            if (magic1 >= 0 && magic2 > magic1) {
                if (mAmPmStyle == AM_PM_STYLE_GONE) {
                    timeFormatted.delete(magic1, magic2 + 1);
                } else {
                    if (mAmPmStyle == AM_PM_STYLE_SMALL) {
                        CharacterStyle style = new RelativeSizeSpan(0.7f);
                        timeFormatted.setSpan(style, magic1, magic2,
                                Spannable.SPAN_EXCLUSIVE_INCLUSIVE);
                    }
                    timeFormatted.delete(magic2, magic2 + 1);
                    timeFormatted.delete(magic1, magic1 + 1);
                }
            }
        }

        CharSequence dateText = null;
        if (mIsStatusBar && mClockDateDisplay != CLOCK_DATE_DISPLAY_GONE) {
            final Date now = mCalendar.getTime();
            CharSequence dateString;
            if (TextUtils.isEmpty(mClockDateFormat)) {
                dateString = DateFormat.format("EEE", now);
            } else {
                try {
                    dateString = DateFormat.format(mClockDateFormat, now);
                } catch (IllegalArgumentException e) {
                    dateString = DateFormat.format("EEE", now);
                }
            }
            String styledDate = dateString.toString();
            if (mClockDateStyle == CLOCK_DATE_STYLE_LOWERCASE) {
                styledDate = styledDate.toLowerCase(Locale.getDefault());
            } else if (mClockDateStyle == CLOCK_DATE_STYLE_UPPERCASE) {
                styledDate = styledDate.toUpperCase(Locale.getDefault());
            }
            dateText = styledDate;
        }

        SpannableStringBuilder formatted = new SpannableStringBuilder();
        if (dateText != null) {
            final boolean dateLeft = mClockDatePosition == STYLE_DATE_LEFT;
            if (dateLeft) {
                formatted.append(dateText).append(' ').append(timeFormatted);
            } else {
                formatted.append(timeFormatted).append(' ').append(dateText);
            }
            if (mClockDateDisplay == CLOCK_DATE_DISPLAY_SMALL) {
                final int dateStart = dateLeft ? 0 : timeFormatted.length() + 1;
                final int dateEnd = dateStart + dateText.length();
                formatted.setSpan(new RelativeSizeSpan(0.7f), dateStart, dateEnd,
                        Spannable.SPAN_EXCLUSIVE_EXCLUSIVE);
            }
        } else {
            formatted.append(timeFormatted);
        }
        return formatted;
    }

    private void applyBoldClockStyle() {
        if (!mIsStatusBar) {
            return;
        }
        Typeface tf = getTypeface();
        if (tf == null) {
            tf = Typeface.DEFAULT;
        }
        final int base = tf.getStyle() & ~Typeface.BOLD;
        final int target = mBoldStatusBarClock ? (base | Typeface.BOLD) : base;
        if (tf.getStyle() != target) {
            setTypeface(Typeface.create(tf, target));
        }
    }
'''
rep(
    "frameworks/base/packages/SystemUI/src/com/android/systemui/statusbar/policy/Clock.java",
    old_tail,
    new_tail,
)

# reloadDimens apply bold
rep(
    "frameworks/base/packages/SystemUI/src/com/android/systemui/statusbar/policy/Clock.java",
    "        if (mShouldApplyPadding) {\n"
    "            // Note: The padding for the clock in the shade is controlled by ShadeHeaderController\n"
    "            // so this just affects the status bar clock.\n"
    "            setPaddingRelative(\n"
    "                    mContext.getResources().getDimensionPixelSize(\n"
    "                            R.dimen.status_bar_clock_starting_padding),\n"
    "                    0,\n"
    "                    mContext.getResources().getDimensionPixelSize(\n"
    "                            R.dimen.status_bar_clock_end_padding),\n"
    "                    0);\n"
    "        }\n"
    "    }\n",
    "        if (mShouldApplyPadding) {\n"
    "            // Note: The padding for the clock in the shade is controlled by ShadeHeaderController\n"
    "            // so this just affects the status bar clock.\n"
    "            setPaddingRelative(\n"
    "                    mContext.getResources().getDimensionPixelSize(\n"
    "                            R.dimen.status_bar_clock_starting_padding),\n"
    "                    0,\n"
    "                    mContext.getResources().getDimensionPixelSize(\n"
    "                            R.dimen.status_bar_clock_end_padding),\n"
    "                    0);\n"
    "        }\n"
    "        applyBoldClockStyle();\n"
    "    }\n",
)

# attrs
rep(
    "frameworks/base/packages/SystemUI/res/values/attrs.xml",
    "        <attr name=\"showDark\" format=\"boolean\" />\n"
    "    </declare-styleable>\n",
    "        <attr name=\"showDark\" format=\"boolean\" />\n"
    "        <attr name=\"isStatusBar\" format=\"boolean\" />\n"
    "    </declare-styleable>\n",
)

# status_bar.xml clock attr
rep(
    "frameworks/base/packages/SystemUI/res/layout/status_bar.xml",
    "                    <com.android.systemui.statusbar.policy.Clock\n"
    "                        android:id=\"@+id/clock\"\n"
    "                        android:layout_width=\"wrap_content\"\n",
    "                    <com.android.systemui.statusbar.policy.Clock\n"
    "                        android:id=\"@+id/clock\"\n"
    "                        systemui:isStatusBar=\"true\"\n"
    "                        android:layout_width=\"wrap_content\"\n",
)
