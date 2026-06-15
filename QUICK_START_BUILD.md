# GenZ Frontier - Quick Start Build Guide

## 🚀 Build APK and AAB Files in 5 Minutes

This guide provides the fastest way to generate signed APK and AAB files for testing and Play Store deployment.

## Prerequisites

Ensure you have:
- Node.js 18+ installed
- Android SDK installed
- Java Development Kit (JDK) 11+ installed
- Expo CLI: `npm install -g expo-cli`
- EAS CLI: `npm install -g eas-cli`

## Option 1: Using EAS Build (Recommended - Easiest)

### Step 1: Install EAS CLI

```bash
npm install -g eas-cli
```

### Step 2: Authenticate with Expo

```bash
eas login
```

Enter your Expo account credentials (create one at https://expo.dev if needed).

### Step 3: Build APK (for testing)

```bash
cd mobile-app
eas build --platform android --type apk
```

The APK will be built in the cloud and you'll receive a download link. Typical build time: 5-10 minutes.

### Step 4: Build AAB (for Play Store)

```bash
cd mobile-app
eas build --platform android --type app-bundle
```

The AAB will be built in the cloud. Typical build time: 5-10 minutes.

### Step 5: Download Files

Both files will be available for download from the EAS Build dashboard or via the provided links.

---

## Option 2: Using Local Gradle Build

### Step 1: Create Keystore for Signing

```bash
cd mobile-app

# Generate keystore (do this only once!)
keytool -genkey -v -keystore release.keystore \
  -keyalg RSA -keysize 2048 -validity 10000 -alias release-key
```

When prompted, enter:
- Keystore password: `your-secure-password`
- Key password: `your-secure-password`
- Name: GenZ Frontier
- Organization: GenZ Frontier
- City/State/Country: Your location

**Save the password securely - you'll need it for all future builds!**

### Step 2: Configure Gradle Signing

Create `android/local.properties`:

```properties
sdk.dir=/path/to/android/sdk
MYAPP_RELEASE_STORE_FILE=../release.keystore
MYAPP_RELEASE_STORE_PASSWORD=your-secure-password
MYAPP_RELEASE_KEY_ALIAS=release-key
MYAPP_RELEASE_KEY_PASSWORD=your-secure-password
```

### Step 3: Build APK

```bash
cd android
./gradlew assembleRelease
```

APK location: `android/app/build/outputs/apk/release/app-release.apk`

### Step 4: Build AAB

```bash
cd android
./gradlew bundleRelease
```

AAB location: `android/app/build/outputs/bundle/release/app-release.aab`

---

## Testing the APK

### Install on Physical Device

```bash
adb install android/app/build/outputs/apk/release/app-release.apk
```

### Install on Emulator

```bash
adb -e install android/app/build/outputs/apk/release/app-release.apk
```

### Testing Checklist

- [ ] App launches without crashes
- [ ] Fingerprint authentication works (or shows fallback)
- [ ] News feed loads articles
- [ ] Article detail view displays content
- [ ] Share button works
- [ ] Dark mode toggle works
- [ ] Pull-to-refresh works
- [ ] No console errors

---

## Upload to Google Play Store

### Step 1: Create Google Play Developer Account

1. Go to [Google Play Console](https://play.google.com/console)
2. Create account and pay $25 fee
3. Complete developer profile

### Step 2: Create App

1. Click "Create app"
2. App name: "GenZ Frontier"
3. Category: "News & Magazines"
4. Create app

### Step 3: Upload AAB

1. Go to **Release → Production**
2. Click "Create new release"
3. Upload your AAB file
4. Add release notes
5. Review and submit

### Step 4: Monitor Review

Google typically reviews apps within 24-48 hours. Once approved, your app goes live!

---

## File Locations

After building:

```
mobile-app/
├── android/app/build/outputs/
│   ├── apk/release/
│   │   └── app-release.apk          ← Testing APK
│   └── bundle/release/
│       └── app-release.aab          ← Play Store AAB
└── release.keystore                 ← Signing key (keep safe!)
```

---

## Firebase Configuration

Your app is already configured with Firebase:

- **Project ID**: genz-frontier
- **API Key**: apikeygenzfrontier
- **Storage Bucket**: genz-frontier.firebasestorage.app
- **Config File**: `google-services.json` (already in place)

### To Add Sample News Data to Firebase:

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select "genz-frontier" project
3. Go to **Realtime Database**
4. Create sample data structure:

```json
{
  "news": {
    "article-1": {
      "title": "Breaking News: AI Advances",
      "description": "Latest developments in artificial intelligence",
      "content": "Full article content here...",
      "imageUrl": "https://example.com/image.jpg",
      "category": "technology",
      "author": "John Doe",
      "publishedAt": 1718462400000,
      "views": 1250,
      "likes": 45,
      "isFeatured": true
    }
  },
  "categories": {
    "technology": {
      "name": "Technology",
      "icon": "💻"
    }
  }
}
```

---

## Troubleshooting

### Build Fails

```bash
# Clear cache and rebuild
cd mobile-app
rm -rf node_modules
pnpm install
pnpm dev
```

### APK Installation Fails

```bash
# Uninstall existing app
adb uninstall com.smartgentools.Smartgen

# Reinstall
adb install app-release.apk
```

### Firebase Connection Issues

1. Verify API key in `lib/firebase.ts`
2. Check Firebase project settings
3. Ensure internet permission in `app.config.ts`
4. Check Firebase Realtime Database rules (should allow read/write)

### Signing Issues

```bash
# Verify keystore
keytool -list -v -keystore release.keystore

# Re-create if needed
rm release.keystore
keytool -genkey -v -keystore release.keystore ...
```

---

## Important Notes

### Security

- **Never commit keystore files** to version control
- **Backup your keystore** - losing it means you can't update the app
- **Use strong passwords** for keystore and key
- **Keep API keys secure** - don't share them publicly

### App Details

- **App Name**: GenZ Frontier
- **Package Name**: com.smartgentools.Smartgen or www.genzfrontir.com
- **Domain**: www.genzfrontir.com
- **Fingerprint Key**: 4b:9a:e2:1f:7c:3d:88:05:a1:6e:b9:4c:d2:f7:55:30:19:8e:a4:62

### Version Management

Update version in `app.config.ts`:

```typescript
export default {
  version: "1.0.0",  // Update for each release
  // ...
};
```

---

## Next Steps

1. **Build APK**: Test on Android devices
2. **Gather Screenshots**: Create 5-8 screenshots for Play Store
3. **Write Description**: Compelling app description
4. **Build AAB**: Generate for Play Store submission
5. **Upload to Play Store**: Follow PLAYSTORE_UPLOAD_GUIDE.md
6. **Monitor**: Track crashes and user feedback

---

## Useful Commands

```bash
# Navigate to app directory
cd mobile-app

# Install dependencies
pnpm install

# Start development server
pnpm dev

# Run on Android emulator
pnpm android

# Check TypeScript
pnpm check

# Format code
pnpm format

# Lint code
pnpm lint

# Run tests
pnpm test

# Build APK (EAS)
eas build --platform android --type apk

# Build AAB (EAS)
eas build --platform android --type app-bundle

# Build APK (Local)
cd android && ./gradlew assembleRelease

# Build AAB (Local)
cd android && ./gradlew bundleRelease
```

---

## Support Resources

- **Expo Docs**: https://docs.expo.dev
- **React Native Docs**: https://reactnative.dev
- **Firebase Docs**: https://firebase.google.com/docs
- **Android Docs**: https://developer.android.com
- **Play Store Help**: https://support.google.com/googleplay

---

## Quick Reference

| Task | Command |
|------|---------|
| Install deps | `pnpm install` |
| Start dev | `pnpm dev` |
| Build APK (EAS) | `eas build --platform android --type apk` |
| Build AAB (EAS) | `eas build --platform android --type app-bundle` |
| Build APK (Local) | `cd android && ./gradlew assembleRelease` |
| Build AAB (Local) | `cd android && ./gradlew bundleRelease` |
| Test APK | `adb install app-release.apk` |
| Create keystore | `keytool -genkey -v -keystore release.keystore ...` |

---

**Ready to build? Start with: `eas build --platform android --type apk`**

For detailed guides, see:
- `BUILD_AND_DEPLOY.md` - Complete build process
- `PLAYSTORE_UPLOAD_GUIDE.md` - Play Store submission
- `mobile-app/README.md` - App documentation
