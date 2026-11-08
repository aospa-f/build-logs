from pathlib import Path

def rep(path, old, new):
    p = Path(path)
    t = p.read_text()
    assert t.count(old) == 1, (path, t.count(old))
    p.write_text(t.replace(old, new, 1))
    print("patched", path)

# LauncherPrefs
rep("src/com/android/launcher3/LauncherPrefs.kt",
    '        @JvmField val DRAWER_OPEN_KEYBOARD = backedUpItem("pref_drawer_open_keyboard", false)\n',
    '        @JvmField val DRAWER_OPEN_KEYBOARD = backedUpItem("pref_drawer_open_keyboard", false)\n'
    '        @JvmField val SEARCH_BAR_BOTTOM = backedUpItem("pref_search_bar_bottom", true)\n')

# Preference
rep("res/xml/launcher_preferences.xml",
    '''        <SwitchPreferenceCompat
            android:key="pref_drawer_show_labels"
            android:title="@string/drawer_show_labels"
            android:defaultValue="true"
            android:persistent="true" />''',
    '''        <SwitchPreferenceCompat
            android:key="pref_search_bar_bottom"
            android:title="@string/search_bar_bottom_title"
            android:summary="@string/search_bar_bottom_summary"
            android:defaultValue="true"
            android:persistent="true" />

        <SwitchPreferenceCompat
            android:key="pref_drawer_show_labels"
            android:title="@string/drawer_show_labels"
            android:defaultValue="true"
            android:persistent="true" />''')

# strings
p = Path("res/values/aospa_strings.xml")
t = p.read_text()
old = '    <string name="pref_themed_icons_summary">Follow themed icons used on home screen</string>\n'
new = old + '''
    <!-- App drawer search bar position -->
    <string name="search_bar_bottom_title">Search bar at bottom</string>
    <string name="search_bar_bottom_summary">Put the app drawer search bar at the bottom. Turn off for the stock top position.</string>
'''
assert t.count(old) == 1
p.write_text(t.replace(old, new, 1))
print("patched strings")

# dimen
p = Path("res/values/dimens.xml")
t = p.read_text()
old = '    <dimen name="all_apps_search_bar_bottom_padding">42dp</dimen>\n'
new = old + '    <dimen name="all_apps_search_bar_bottom_margin">16dp</dimen>\n'
assert t.count(old) == 1
p.write_text(t.replace(old, new, 1))
print("patched dimens")

# Activity: add bottom setup
rep("src/com/android/launcher3/allapps/ActivityAllAppsContainerView.java",
    '''        mSearchContainer = inflateSearchBar();
        if (!isSearchBarFloating()) {
            // Add the search box above everything else in this container (if the flag is enabled,
            // it's added to drag layer in onAttach instead).
            addView(mSearchContainer);
            // The search container is visually at the top of the all apps UI, and should thus be
            // focused by default. It's added to end of the children list, so it needs to be
            // explicitly marked as focused by default.
            mSearchContainer.setFocusedByDefault(true);
        }
        mSearchUiManager = (SearchUiManager) mSearchContainer;''',
    '''        mSearchContainer = inflateSearchBar();
        if (!isSearchBarFloating()) {
            // Add the search box above everything else in this container (if the flag is enabled,
            // it's added to drag layer in onAttach instead).
            addView(mSearchContainer);
            // The search container is visually at the top of the all apps UI, and should thus be
            // focused by default. It's added to end of the children list, so it needs to be
            // explicitly marked as focused by default.
            mSearchContainer.setFocusedByDefault(true);
            if (isSearchBarAtBottom()) {
                layoutSearchBarAtBottom();
            }
        }
        mSearchUiManager = (SearchUiManager) mSearchContainer;''')

# applyAdapters layout branch
rep("src/com/android/launcher3/allapps/ActivityAllAppsContainerView.java",
    '''        removeCustomRules(rvContainer);
        removeCustomRules(getSearchRecyclerView());
        if (isSearchBarFloating()) {
            alignParentTop(rvContainer, showTabs);
            alignParentTop(getSearchRecyclerView(), /* tabs= */ false);
        } else {
            layoutBelowSearchContainer(rvContainer, showTabs);
            layoutBelowSearchContainer(getSearchRecyclerView(), /* tabs= */ false);
        }''',
    '''        removeCustomRules(rvContainer);
        removeCustomRules(getSearchRecyclerView());
        if (isSearchBarAtBottom()) {
            layoutAboveSearchContainer(rvContainer, showTabs);
            layoutAboveSearchContainer(getSearchRecyclerView(), /* tabs= */ false);
        } else if (isSearchBarFloating()) {
            alignParentTop(rvContainer, showTabs);
            alignParentTop(getSearchRecyclerView(), /* tabs= */ false);
        } else {
            layoutBelowSearchContainer(rvContainer, showTabs);
            layoutBelowSearchContainer(getSearchRecyclerView(), /* tabs= */ false);
        }''')

# setupHeader branch
rep("src/com/android/launcher3/allapps/ActivityAllAppsContainerView.java",
    '''        removeCustomRules(mHeader);
        if (isSearchBarFloating()) {
            alignParentTop(mHeader, false /* includeTabsMargin */);
        } else {
            layoutBelowSearchContainer(mHeader, false /* includeTabsMargin */);
        }''',
    '''        removeCustomRules(mHeader);
        if (isSearchBarAtBottom()) {
            alignParentTop(mHeader, false /* includeTabsMargin */);
        } else if (isSearchBarFloating()) {
            alignParentTop(mHeader, false /* includeTabsMargin */);
        } else {
            layoutBelowSearchContainer(mHeader, false /* includeTabsMargin */);
        }''')

# methods before layoutBelowSearchContainer
rep("src/com/android/launcher3/allapps/ActivityAllAppsContainerView.java",
    '    private void layoutBelowSearchContainer(View v, boolean includeTabsMargin) {',
    '''    private boolean isSearchBarAtBottom() {
        return com.android.launcher3.LauncherPrefs.SEARCH_BAR_BOTTOM.get(
                mActivityContext.asContext());
    }

    private void layoutSearchBarAtBottom() {
        if (mSearchContainer.getLayoutParams() instanceof RelativeLayout.LayoutParams layoutParams) {
            layoutParams.addRule(RelativeLayout.ALIGN_PARENT_BOTTOM);
            layoutParams.addRule(RelativeLayout.CENTER_HORIZONTAL);
            layoutParams.topMargin = 0;
            layoutParams.bottomMargin = getResources().getDimensionPixelSize(
                    R.dimen.all_apps_search_bar_bottom_margin);
            mSearchContainer.setLayoutParams(layoutParams);
        }
    }

    private void layoutAboveSearchContainer(View v, boolean includeTabsMargin) {
        if (!(v.getLayoutParams() instanceof RelativeLayout.LayoutParams)) {
            return;
        }

        RelativeLayout.LayoutParams layoutParams = (LayoutParams) v.getLayoutParams();
        layoutParams.addRule(RelativeLayout.ALIGN_PARENT_TOP);
        layoutParams.addRule(RelativeLayout.ABOVE, R.id.search_container_all_apps);
        layoutParams.topMargin = includeTabsMargin
                ? getContext().getResources().getDimensionPixelSize(
                        R.dimen.all_apps_header_pill_height)
                : 0;
    }

    private void layoutBelowSearchContainer(View v, boolean includeTabsMargin) {''')
