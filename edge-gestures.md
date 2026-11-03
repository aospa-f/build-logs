# Axion edge gestures and separate QS routing

This document covers the edge volume / top-edge panel gestures and the
separate notification/Quick Settings shade routing added on the `calcite`
branch for `giulia`.

## Edge zones

Screen height is split into three vertical zones on both the left and right
edges (display coordinates, so landscape works with the rotated bounds):

| Zone | Height | Gesture |
| --- | --- | --- |
| Top | 0 – 32% | Swipe down: left edge opens notifications, right edge opens QS |
| Volume | 34 – 82% | Slide up increases media volume, slide down decreases it |
| Bottom | 82 – 100% | Reserved for system gestures |

The edge hit width is the normal back-gesture width plus 8dp of slack. Volume
changes happen in 24dp steps. Both edges behave identically.

## Volume bubble

While an edge volume gesture is active the system volume panel is suppressed
(`adjustStreamVolume(..., flags = 0)`). A 56dp Material 3 circle is shown at
the active screen edge, vertically centred, with the volume percentage inside.
The bubble is a non-touchable `TYPE_VOLUME_OVERLAY` window owned by SystemUI
and fades out 650ms after the gesture ends. It moves to the other edge when a
gesture starts there.

## Settings

System → Gestures contains two new pages:

- **Edge volume gestures** (`AxEdgeVolumeGestureSettings`)
- **Notification & Quick Settings gestures** (`AxEdgePanelGestureSettings`)

Each page has an enable switch and a **Blocked apps** entry that opens a
full-screen app list (`AxEdge*BlocklistSettings`) with one switch per
launchable app. Selections are stored immediately in `Settings.Secure`:

- `ax_edge_volume_enabled` / `ax_edge_volume_blocked_apps`
- `ax_edge_panel_enabled` / `ax_edge_panel_blocked_apps`

`ax_edge_*_enabled` defaults to 1. Blocked lists are comma-separated package
names. SystemUI reads both on every gesture-down, so changes take effect
without a restart.

## Separate shade QS routing

In `SEPARATE` panel mode the right half of the screen (or the left half when
`ax_qs_quick_panel_on_left=1`) is the Quick Settings side.

Fixes that make QS pulls deterministic:

1. `isOpenQsEvent()` no longer requires `mBarState == SHADE`; the QS half works
   on the lock screen.
2. `shouldQuickSettingsIntercept()` treats the QS half as QS even when the
   shade is collapsed, which keeps the keyguard pulse-expansion handler from
   stealing the gesture.
3. A keyguard QS-side `ACTION_DOWN` is intercepted by the shade window before
   the lock-screen drag handler.
4. A QS-side `ACTION_DOWN` latches QS expansion even while a previous shade is
   still collapsing, so fast follow-up pulls cannot fall back to the
   notification page.
5. The latch is cleared on a non-QS gesture and when a collapsed gesture ends
   with a tap, so a previous tap cannot change the next notification pull.

Once the notification page is fully open, the QS-half shortcut stops applying:
taps and scrolling on notifications keep working normally. Switching pages is
still done with the horizontal page swipe.

In landscape the shade uses the split-shade layout (QS left, notifications
right), so either top-edge gesture opens that combined shade.

## Verification

- QS half on home / lock screen: repeated fresh pulls, including while a
  previous shade is still closing.
- Notification half on home / lock screen / in apps.
- Horizontal page swipes both directions.
- Volume up/down on both edges, portrait and landscape, with the bubble on the
  active edge.
- Top-edge panel gestures on home, lock screen and inside apps.
- Per-app blocking for both gestures and the enable switches.
