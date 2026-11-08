from pathlib import Path

def rep(path, old, new):
    p = Path(path)
    t = p.read_text()
    assert t.count(old) == 1, (path, t.count(old))
    p.write_text(t.replace(old, new, 1))
    print("patched", path)

rep("quickstep/src/com/android/launcher3/QuickstepTransitionManager.java",
    "    public static final long APP_LAUNCH_DURATION = 420;\n",
    "    public static final long APP_LAUNCH_DURATION = 380;\n")
rep("quickstep/src/com/android/launcher3/QuickstepTransitionManager.java",
    "    private static final int CLOSING_TRANSITION_DURATION_MS = 300;\n",
    "    private static final int CLOSING_TRANSITION_DURATION_MS = 270;\n")

old_spring = '''    /**
     * Damped-harmonic-oscillator interpolator used to give the app-open/close morph a
     * "fluid" spring feel (OxygenOS-style) instead of a static Material easing curve.
     * getInterpolation(0) == 0 and getInterpolation(1) settles to ~1 with a small
     * decaying overshoot, controlled by dampingRatio (lower = bouncier) and
     * numOfCycles (higher = faster settling oscillation).
     */
    private static final class SpringInterpolator implements Interpolator {
        private final double mDampingRatio;
        private final double mNumOfCycles;

        SpringInterpolator(double dampingRatio, double numOfCycles) {
            mDampingRatio = dampingRatio;
            mNumOfCycles = numOfCycles;
        }

        @Override
        public float getInterpolation(float input) {
            double wn = mNumOfCycles * 2 * Math.PI;
            double wd = wn * Math.sqrt(Math.max(1e-6, 1 - mDampingRatio * mDampingRatio));
            double envelope = Math.exp(-mDampingRatio * wn * input);
            return (float) (1 - envelope * (Math.cos(wd * input)
                    + (mDampingRatio * wn / wd) * Math.sin(wd * input)));
        }
    }
'''
new_spring = '''    /**
     * Damped-harmonic-oscillator interpolator for a subtle OEM-style spring bounce.
     */
    private static final class SpringInterpolator implements Interpolator {
        private static final int TABLE_SIZE = 256;
        private final float[] mTable = new float[TABLE_SIZE];

        SpringInterpolator(double dampingRatio, double numOfCycles) {
            double wn = numOfCycles * 2 * Math.PI;
            double dSq = 1 - dampingRatio * dampingRatio;
            double wd = wn * Math.sqrt(Math.max(1e-9, dSq));
            for (int i = 0; i < TABLE_SIZE; i++) {
                double t = (double) i / (TABLE_SIZE - 1);
                double envelope = Math.exp(-dampingRatio * wn * t);
                mTable[i] = (float) (1.0 - envelope * (
                        Math.cos(wd * t) + (dampingRatio * wn / wd) * Math.sin(wd * t)));
            }
        }

        @Override
        public float getInterpolation(float input) {
            if (input <= 0f) return mTable[0];
            if (input >= 1f) return mTable[TABLE_SIZE - 1];
            float idx = input * (TABLE_SIZE - 1);
            int lo = (int) idx;
            float frac = idx - lo;
            return mTable[lo] + frac * (mTable[lo + 1] - mTable[lo]);
        }
    }
'''
rep("quickstep/src/com/android/launcher3/QuickstepTransitionManager.java", old_spring, new_spring)

old_props = '''            FloatProp mDx = new FloatProp(0, prop.dX, mOpeningXInterpolator);
            FloatProp mDy = new FloatProp(0, prop.dY);

            FloatProp mIconScaleToFitScreen = new FloatProp(prop.initialAppIconScale,
                    prop.finalAppIconScale);
            FloatProp mIconAlpha = new FloatProp(prop.iconAlphaStart, 0f,
                    clampToDuration(LINEAR, APP_LAUNCH_ALPHA_START_DELAY, APP_LAUNCH_ALPHA_DURATION,
                            APP_LAUNCH_DURATION));

            FloatProp mWindowRadius =
                    new FloatProp(initialWindowRadius, getWindowCornerRadius(mLauncher));
            FloatProp mShadowRadius = new FloatProp(0, finalShadowRadius);

            FloatProp mCropRectCenterX = new FloatProp(prop.cropCenterXStart, prop.cropCenterXEnd);
            FloatProp mCropRectCenterY = new FloatProp(prop.cropCenterYStart, prop.cropCenterYEnd);
            FloatProp mCropRectWidth = new FloatProp(prop.cropWidthStart, prop.cropWidthEnd);
            FloatProp mCropRectHeight = new FloatProp(prop.cropHeightStart, prop.cropHeightEnd);
'''
new_props = '''            // Horizontal translation stays flat so it settles with the vertical axis.
            FloatProp mDx = new FloatProp(0, prop.dX, DECELERATE_1_5);
            FloatProp mDy = new FloatProp(0, prop.dY, DECELERATE_1_5);

            FloatProp mIconScaleToFitScreen = new FloatProp(prop.initialAppIconScale,
                    prop.finalAppIconScale);
            FloatProp mIconAlpha = new FloatProp(prop.iconAlphaStart, 0f,
                    clampToDuration(LINEAR, APP_LAUNCH_ALPHA_START_DELAY, APP_LAUNCH_ALPHA_DURATION,
                            APP_LAUNCH_DURATION));

            // Only the icon-grow scale gets the spring bounce. Corner radius, shadow and
            // crop rect stay flat so overshoot does not wobble the visible window edges.
            FloatProp mWindowRadius =
                    new FloatProp(initialWindowRadius, getWindowCornerRadius(mLauncher),
                            DECELERATE_1_5);
            FloatProp mShadowRadius = new FloatProp(0, finalShadowRadius, DECELERATE_1_5);

            FloatProp mCropRectCenterX = new FloatProp(prop.cropCenterXStart, prop.cropCenterXEnd,
                    DECELERATE_1_5);
            FloatProp mCropRectCenterY = new FloatProp(prop.cropCenterYStart, prop.cropCenterYEnd,
                    DECELERATE_1_5);
            FloatProp mCropRectWidth = new FloatProp(prop.cropWidthStart, prop.cropWidthEnd,
                    DECELERATE_1_5);
            FloatProp mCropRectHeight = new FloatProp(prop.cropHeightStart, prop.cropHeightEnd,
                    DECELERATE_1_5);
'''
rep("quickstep/src/com/android/launcher3/QuickstepTransitionManager.java", old_props, new_props)

old_blur = '''            FloatProp mBlurRadius = new FloatProp(0f, mMaxBlurRadius, DECELERATE_1_5);
            FloatProp mBlurScrimAlpha = new FloatProp(0f, scrimAlpha, DECELERATE_1_5);
'''
new_blur = '''            // Blur fades over the first 75% of the animation so the GPU is free during
            // the heaviest crop-rect phase at the end.
            FloatProp mBlurRadius = new FloatProp(0f, mMaxBlurRadius, clampToDuration(
                    DECELERATE_1_5, 0, (long) (APP_LAUNCH_DURATION * 0.75f),
                    APP_LAUNCH_DURATION));
            FloatProp mBlurScrimAlpha = new FloatProp(0f, scrimAlpha, clampToDuration(
                    DECELERATE_1_5, 0, (long) (APP_LAUNCH_DURATION * 0.75f),
                    APP_LAUNCH_DURATION));
'''
rep("quickstep/src/com/android/launcher3/QuickstepTransitionManager.java", old_blur, new_blur)

old_recalc = '''                    mCropRectCenterY = new FloatProp(prop.cropCenterYStart, prop.cropCenterYEnd);
                    mCropRectHeight = new FloatProp(prop.cropHeightStart, prop.cropHeightEnd);
                    mDy = new FloatProp(0, prop.dY);
                    mIconScaleToFitScreen = new FloatProp(prop.initialAppIconScale,
                            prop.finalAppIconScale);
                    float interpolatedPercent = getDefaultInterpolator().getInterpolation(percent);
'''
new_recalc = '''                    mCropRectCenterY = new FloatProp(prop.cropCenterYStart, prop.cropCenterYEnd,
                            DECELERATE_1_5);
                    mCropRectHeight = new FloatProp(prop.cropHeightStart, prop.cropHeightEnd,
                            DECELERATE_1_5);
                    mDy = new FloatProp(0, prop.dY, DECELERATE_1_5);
                    mIconScaleToFitScreen = new FloatProp(prop.initialAppIconScale,
                            prop.finalAppIconScale);
                    float interpolatedPercent = DECELERATE_1_5.getInterpolation(percent);
'''
rep("quickstep/src/com/android/launcher3/QuickstepTransitionManager.java", old_recalc, new_recalc)

rep("quickstep/src/com/android/launcher3/QuickstepTransitionManager.java",
    '''            final FloatProp mDx = new FloatProp(widgetBackgroundBounds.centerX(),
                    windowTargetBounds.centerX(), mOpeningXInterpolator);''',
    '''            final FloatProp mDx = new FloatProp(widgetBackgroundBounds.centerX(),
                    windowTargetBounds.centerX(), DECELERATE_1_5);''')

rep("quickstep/res/values/config.xml",
    '    <dimen name="max_depth_blur_radius_enhanced">30dp</dimen>\n',
    '    <dimen name="max_depth_blur_radius_enhanced">18dp</dimen>\n')
