# Vendor HAL fixes — 2026-11-01

Build: `aospa_giulia-userdebug` (calcite, test-keys)
Result: **success** (24:17)
OTA: `out/target/product/giulia/aospa-calcite-unofficial-giulia-20261101.zip`

## Phone-confirmed vendor failures

### 1. OPlus sensor feature service (`vendor.oplusSensor-aidl-1`)

Live phone log:

```
F/linker: CANNOT LINK EXECUTABLE "/odm/bin/hw/vendor-oplus-hardware-oplusSensor-V1-service":
library "libdumpstateutil.so" not found
```

`libdumpstateutil.so` exists in `/system/lib64`, but it is system-only and not
visible in the vendor linker namespace. The binary references none of that
library's exported symbols, so the DT_NEEDED entry was stale.

Fix: `patchelf --remove-needed libdumpstateutil.so` on the prebuilt service.
Verified on device: the patched service starts, stays running and registers
`vendor.oplus.hardware.oplusSensor.ISensorFeature/default`.

Commit: `aospa-f/device_oneplus_giulia` `e423295`

### 2. Missing OPlus face HAL

Phone logs showed 206 repeated failures:

```
E/init: Control message: Could not find
'aidl/android.hardware.biometrics.face.virtualhal.IVirtualHal/virtual'
E/BiometricServiceRegistry: No sensors found
```

The TheMuppets `vendor/oneplus/giulia` tree contains the face HAL binary,
`libstfaceunlockocl_uff.so`, the ODM VINTF manifest and the init rc, but its
generated makefile never installed them. `libcamera2ndk_vendor.so` and
`android.hardware.biometrics.face-V3-ndk.so` were also absent.

Fix: install the face binary/library/manifest/rc as device prebuilts, add the
face and camera NDK dependencies, and pull the vendor variants explicitly via
`shared_libs`.

Commits: `aospa-f/device_oneplus_giulia` `38b600a`, `72c9826`

### 3. OPlus sensor service auto-start

The stock rc is `disabled` and only starts on
`ro.vendor.oplus.sensor.lowmem=` / `=false`, which never fired. Add
`init.oplusSensor.rc` with an `on boot` start and set the vendor property.

Commit: `aospa-f/device_oneplus_giulia` `38b600a`

### 4. Settings javac failures

```
AppVolumePanel.java:45: error: cannot find symbol R.string.app_volume
BluetoothDetailsCodecController.java: cannot find symbol
bluetooth_details_audio_codec_title / bluetooth_details_audio_codec_unavailable
```

Fix: add the missing strings to `res/values/aospa_strings.xml`.

Commit: `aospa-f/aospa_packages_apps_Settings` `aadbcc5ce6f`

### 5. Prebuilt ELF policy

`libiccprofile.so`, `liboemcrypto.so` and the OPlus sensor service were copied
through `PRODUCT_COPY_FILES`, which the build rejects as ELF prebuilts. Convert
them to `cc_prebuilt_library_shared` / `cc_prebuilt_binary` and remove
`BUILD_BROKEN_ELF_PREBUILT_PRODUCT_COPY_FILES`.

Commit: `aospa-f/device_oneplus_giulia` `d11b34e`

### 6. Duplicate file_contexts entry

`hardware/oplus/sepolicy/qti/vendor/file_contexts` contained the same
`display.mapper@.*.so` rule twice, failing `file_contexts.device.sorted.tmp`
with `Multiple same specifications`.

Commit: `aospa-f/hardware_oplus` `cbd99b9`

## Build verification

- `odm/bin/hw/vendor.oplus.hardware.biometrics.face@1.0-service_uff`
- `odm/lib64/libstfaceunlockocl_uff.so`
- `odm/etc/vintf/manifest/manifest_oplus_face.xml`
- `odm/etc/vintf/manifest/manifest_oplusSensor_aidl.xml`
- `odm/etc/init/vendor.oplus.hardware.biometrics.face@1.0-service.rc`
- `odm/etc/init/init.oplus.face.rc`
- `odm/bin/hw/vendor-oplus-hardware-oplusSensor-V1-service` — no
  `libdumpstateutil.so` in `DT_NEEDED`
- `vendor/lib64/libcamera2ndk_vendor.so`
- `vendor/lib64/android.hardware.biometrics.face-V3-ndk.so`
- `vendor/etc/init/init.oplusSensor.rc`
- `vendor/build.prop` contains `ro.vendor.oplus.sensor.lowmem=false`
- Settings APK contains `app_volume`,
  `bluetooth_details_audio_codec_title` and
  `bluetooth_details_audio_codec_unavailable`
- SELinux: face service is `hal_oplus_face_exec`; sensor service is
  `hal_oplus_sensor_aidl_exec`
