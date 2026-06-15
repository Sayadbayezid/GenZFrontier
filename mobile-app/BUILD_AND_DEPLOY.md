# GenZ Frontier News App - Build and Deployment Guide

This guide covers building, signing, and deploying the GenZ Frontier news app to the Google Play Store.

## Prerequisites

Before you begin, ensure you have the following:

- Node.js 18+ and npm/pnpm installed
- Android SDK and Android Studio installed
- Java Development Kit (JDK) 11 or higher
- A Google Play Developer account
- Firebase project set up (genz-frontier)
- Your domain: www.genzfrontir.com
- Fingerprint key: `4b:9a:e2:1f:7c:3d:88:05:a1:6e:b9:4c:d2:f7:55:30:19:8e:a4:62`

## Step 1: Install Dependencies

```bash
cd mobile-app
pnpm install
```

## Step 2: Configure Firebase

The Firebase configuration is already set up in `google-services.json` and `lib/firebase.ts`. The configuration includes:

- Project ID: `genz-frontier`
- Storage Bucket: `genz-frontier.firebasestorage.app`
- API Key: `apikeygenzfrontier`

## Step 3: Create Android Keystore

To sign your APK and AAB files, you need to create a keystore file:

```bash
keytool -genkey -v -keystore release.keystore -keyalg RSA -keysize 2048 -validity 10000 -alias release-key
```

When prompted, enter:
- **Keystore password**: Your secure password (save this!)
- **Key password**: Same as keystore password (recommended)
- **First and Last Name**: GenZ Frontier
- **Organizational Unit**: News
- **Organization**: GenZ Frontier
- **City**: Your city
- **State**: Your state
- **Country Code**: Your country code (e.g., US)

Save the `release.keystore` file securely - you'll need it for all future builds.

## Step 4: Configure Signing in app.config.ts

Update your `app.config.ts` with the signing configuration:

```typescript
android: {
  // ... other config
  signingConfig: {
    keyAlias: 'release-key',
    keyPassword: 'YOUR_KEY_PASSWORD',
    storeFile: './release.keystore',
    storePassword: 'YOUR_KEYSTORE_PASSWORD',
  },
}
```

## Step 5: Build APK for Testing

To generate a signed APK for testing on Android devices:

```bash
# Using EAS (Expo Application Services)
eas build --platform android --type apk

# Or using local Gradle
./gradlew assembleRelease
```

The APK will be generated at:
```
android/app/build/outputs/apk/release/app-release.apk
```

## Step 6: Build AAB for Play Store

To generate an Android App Bundle (AAB) for Play Store distribution:

```bash
# Using EAS
eas build --platform android --type app-bundle

# Or using local Gradle
./gradlew bundleRelease
```

The AAB will be generated at:
```
android/app/build/outputs/bundle/release/app-release.aab
```

## Step 7: Test the APK

Before uploading to Play Store, test the APK on a real Android device:

```bash
# Connect your Android device via USB
adb install android/app/build/outputs/apk/release/app-release.apk

# Or use Android Studio to install and test
```

### Testing Checklist

- [ ] App launches without crashes
- [ ] Fingerprint authentication works
- [ ] News feed loads and displays articles
- [ ] Article detail view works
- [ ] Share functionality works
- [ ] Dark mode toggle works
- [ ] Pull-to-refresh works
- [ ] Category filtering works
- [ ] Offline functionality works (if implemented)

## Step 8: Prepare Play Store Listing

### Create App on Google Play Console

1. Go to [Google Play Console](https://play.google.com/console)
2. Click "Create app"
3. Enter app name: "GenZ Frontier"
4. Select category: "News & Magazines"
5. Fill in required information

### App Details

- **App name**: GenZ Frontier
- **Short description**: Stay updated with the latest news from GenZ Frontier
- **Full description**: 
  ```
  GenZ Frontier is your go-to news app for staying updated with the latest 
  stories from around the world. Get real-time news updates, read in-depth 
  articles, and customize your news feed based on your interests.
  
  Features:
  - Real-time news updates
  - Multiple news categories
  - Biometric authentication (fingerprint/face recognition)
  - Dark mode support
  - Offline reading
  - Share articles with friends
  - Bookmark your favorite articles
  
  Visit us at: www.genzfrontir.com
  ```

### Screenshots

Prepare screenshots (1080x1920px) for:
- Home screen with news feed
- Article detail view
- Search functionality
- Settings screen
- Dark mode view

### Icon and Graphics

- **App icon**: 512x512px (already generated)
- **Feature graphic**: 1024x500px
- **Promo graphic**: 180x120px

### Privacy Policy

Create a privacy policy at: `https://www.genzfrontir.com/privacy-policy.html`

### Permissions

The app requests:
- `POST_NOTIFICATIONS` - For push notifications
- `USE_FINGERPRINT` - For biometric authentication
- `USE_BIOMETRIC` - For biometric authentication
- Internet access - For fetching news from Firebase

## Step 9: Upload to Play Store

### Upload APK/AAB

1. Go to Google Play Console → Your app → Release → Production
2. Click "Create new release"
3. Upload the AAB file (or APK if using internal testing)
4. Add release notes:
   ```
   Version 1.0.0 - Initial Release
   
   - Launch of GenZ Frontier news app
   - Real-time news updates from Firebase
   - Biometric authentication support
   - Dark mode and light mode
   - Article sharing and bookmarking
   - Multiple news categories
   ```

### Set Content Rating

1. Go to Content rating → Fill out questionnaire
2. Get content rating certificate

### Pricing and Distribution

1. Set pricing to Free
2. Select countries where app is available
3. Accept Google Play policies

### Review and Publish

1. Review all information
2. Click "Review release"
3. Click "Rollout to production"

The app will be reviewed by Google (typically 24-48 hours) before going live.

## Step 10: Monitor and Update

After publishing:

1. **Monitor crashes**: Check Play Console → Android vitals
2. **Read reviews**: Respond to user feedback
3. **Update regularly**: Push new features and bug fixes
4. **Track analytics**: Monitor user engagement and retention

## Building with EAS (Recommended)

For easier builds without local setup, use Expo Application Services (EAS):

```bash
# Install EAS CLI
npm install -g eas-cli

# Login to Expo
eas login

# Build APK
eas build --platform android --type apk

# Build AAB
eas build --platform android --type app-bundle

# Submit to Play Store
eas submit --platform android
```

## Troubleshooting

### Build Fails

- Clear cache: `pnpm install --force`
- Check Java version: `java -version`
- Update Android SDK: Open Android Studio → SDK Manager

### APK Installation Fails

- Check device Android version (minimum API 24)
- Clear app data: `adb shell pm clear com.smartgentools.Smartgen`
- Reinstall: `adb uninstall com.smartgentools.Smartgen`

### Firebase Connection Issues

- Verify API key in `lib/firebase.ts`
- Check Firebase project settings
- Ensure internet permission in `app.config.ts`

### Signing Issues

- Verify keystore password
- Check keystore file path
- Ensure JDK is properly installed

## Security Notes

- **Never commit keystore files** to version control
- **Secure your passwords** - use environment variables
- **Backup your keystore** - losing it means you can't update the app
- **Use strong passwords** for keystore and key

## Support

For issues or questions:
- Check Firebase documentation: https://firebase.google.com/docs
- Expo documentation: https://docs.expo.dev
- Google Play Console help: https://support.google.com/googleplay

## Next Steps

1. Set up continuous deployment with GitHub Actions
2. Implement analytics tracking
3. Set up crash reporting with Sentry or Firebase Crashlytics
4. Create a beta testing program
5. Plan feature roadmap based on user feedback
