# GenZ Frontier News App

A professional, feature-rich news reading application built with React Native and Expo, featuring Firebase integration, biometric authentication, and real-time news updates.

## 🌟 Features

- **Real-Time News Updates**: Get instant notifications about breaking news
- **Biometric Authentication**: Secure fingerprint/face recognition login
- **Multiple Categories**: Technology, Business, Entertainment, Sports, and more
- **Dark Mode**: Comfortable reading experience with light and dark themes
- **Article Sharing**: Share stories across social media platforms
- **Bookmarking**: Save articles for later reading
- **Offline Support**: Read downloaded articles without internet
- **Search Functionality**: Find articles by keywords
- **Responsive Design**: Optimized for all Android devices

## 📱 Tech Stack

- **Framework**: React Native with Expo SDK 54
- **Language**: TypeScript 5.9
- **Styling**: NativeWind (Tailwind CSS for React Native)
- **Backend**: Firebase (Authentication, Realtime Database, Storage)
- **State Management**: React Context + AsyncStorage
- **Navigation**: Expo Router
- **Authentication**: Firebase Auth + Expo Local Authentication (Biometrics)
- **Build Tool**: EAS Build (Expo Application Services)

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm/pnpm
- Android SDK and Android Studio
- Java Development Kit (JDK) 11+
- Expo CLI: `npm install -g expo-cli`

### Installation

```bash
# Navigate to mobile app directory
cd mobile-app

# Install dependencies
pnpm install

# Start development server
pnpm dev
```

### Running on Device

```bash
# Scan QR code with Expo Go app on your Android device
# Or start Android emulator
pnpm android

# For iOS (requires macOS)
pnpm ios
```

## 📁 Project Structure

```
mobile-app/
├── app/                          # Expo Router app directory
│   ├── (tabs)/                   # Tab navigation
│   │   ├── _layout.tsx           # Tab bar configuration
│   │   └── index.tsx             # Home screen (news feed)
│   ├── _layout.tsx               # Root layout with providers
│   ├── news-detail.tsx           # Article detail screen
│   └── oauth/                    # OAuth callbacks
├── lib/
│   ├── firebase.ts               # Firebase configuration
│   ├── services/
│   │   ├── news-service.ts       # News fetching logic
│   │   └── auth-service.ts       # Authentication logic
│   ├── trpc.ts                   # tRPC client
│   └── utils.ts                  # Utility functions
├── components/
│   ├── screen-container.tsx      # SafeArea wrapper
│   ├── themed-view.tsx           # Theme-aware view
│   └── ui/                       # UI components
├── hooks/
│   ├── use-colors.ts             # Theme colors hook
│   ├── use-auth.ts               # Auth state hook
│   └── use-color-scheme.ts       # Dark/light mode detection
├── assets/
│   └── images/                   # App icons and images
├── theme.config.js               # Tailwind color configuration
├── app.config.ts                 # Expo app configuration
├── google-services.json          # Firebase configuration
└── package.json                  # Dependencies

server/                           # Backend (Express + tRPC)
├── _core/
│   ├── index.ts                  # Server entry point
│   ├── trpc.ts                   # tRPC router setup
│   └── ...                       # Other server modules
└── README.md                     # Backend documentation
```

## 🔧 Configuration

### Firebase Setup

Firebase configuration is in `lib/firebase.ts` and `google-services.json`:

```typescript
// lib/firebase.ts
const firebaseConfig = {
  apiKey: 'AIzaSyAU6ymfgej2yZ5YoDulBf6smcvWLcB6x4w',
  projectId: 'genz-frontier',
  storageBucket: 'genz-frontier.firebasestorage.app',
  // ... other config
};
```

### App Configuration

Update `app.config.ts` with your app details:

```typescript
const env = {
  appName: 'GenZ Frontier',
  appSlug: 'genz-frontier',
  logoUrl: 'https://...', // Your logo URL
  // ... other config
};
```

### Theme Customization

Edit `theme.config.js` to change colors:

```javascript
const themeColors = {
  primary: { light: '#0066CC', dark: '#0066CC' },
  secondary: { light: '#FF6B35', dark: '#FF8C42' },
  // ... other colors
};
```

## 🔐 Authentication

The app supports two authentication methods:

### 1. Biometric Authentication (Fingerprint/Face ID)

```typescript
import { authService } from '@/lib/services/auth-service';

// Authenticate with biometric
const success = await authService.authenticateWithBiometric();

// Sign in with saved biometric credentials
const user = await authService.signInWithBiometric();
```

### 2. Email/Password Authentication

```typescript
// Sign up
const user = await authService.signUp(email, password, displayName);

// Sign in
const user = await authService.signIn(email, password);

// Sign out
await authService.signOut();
```

## 📰 News Service

Fetch and manage news articles:

```typescript
import { newsService } from '@/lib/services/news-service';

// Get all articles
const articles = await newsService.getArticles(50);

// Get articles by category
const techNews = await newsService.getArticlesByCategory('technology', 50);

// Search articles
const results = await newsService.searchArticles('AI');

// Get featured articles
const featured = await newsService.getFeaturedArticles(10);

// Subscribe to real-time updates
const unsubscribe = newsService.subscribeToArticles((articles) => {
  console.log('Articles updated:', articles);
});
```

## 🎨 Styling

The app uses NativeWind (Tailwind CSS for React Native):

```tsx
<View className="flex-1 items-center justify-center p-4">
  <Text className="text-2xl font-bold text-foreground">
    Hello World
  </Text>
  <Text className="mt-2 text-muted">
    Subtitle text
  </Text>
</View>
```

Available color tokens:
- `primary` - Main brand color
- `secondary` - Accent color
- `background` - Screen background
- `surface` - Card/container background
- `foreground` - Primary text
- `muted` - Secondary text
- `border` - Borders and dividers
- `success` - Success states
- `warning` - Warning states
- `error` - Error states

## 📦 Building for Production

### Generate APK (for testing)

```bash
cd mobile-app
eas build --platform android --type apk
```

### Generate AAB (for Play Store)

```bash
cd mobile-app
eas build --platform android --type app-bundle
```

See `BUILD_AND_DEPLOY.md` for detailed build instructions.

## 🚀 Deployment

### Google Play Store

1. Create signed APK/AAB
2. Set up Google Play Developer account
3. Follow `PLAYSTORE_UPLOAD_GUIDE.md`
4. Submit app for review
5. Monitor and respond to user feedback

### Direct APK Distribution

Share the signed APK file directly with users for testing.

## 🧪 Testing

### Unit Tests

```bash
pnpm test
```

### Manual Testing Checklist

- [ ] App launches without crashes
- [ ] Biometric authentication works
- [ ] News feed loads and displays articles
- [ ] Article detail view works
- [ ] Share functionality works
- [ ] Dark mode toggle works
- [ ] Pull-to-refresh works
- [ ] Category filtering works
- [ ] Search functionality works
- [ ] Offline reading works

## 📊 Firebase Database Structure

```
genz-frontier/
├── news/
│   ├── article-id-1/
│   │   ├── title: string
│   │   ├── description: string
│   │   ├── content: string
│   │   ├── imageUrl: string
│   │   ├── category: string
│   │   ├── author: string
│   │   ├── publishedAt: timestamp
│   │   ├── views: number
│   │   ├── likes: number
│   │   └── isFeatured: boolean
│   └── ...
├── categories/
│   ├── technology/
│   │   ├── name: string
│   │   └── icon: string
│   └── ...
└── users/
    ├── user-id-1/
    │   ├── email: string
    │   ├── displayName: string
    │   ├── favorites: array
    │   └── preferences: object
    └── ...
```

## 🔒 Security

- **Biometric Authentication**: Uses device secure enclave
- **Secure Storage**: Credentials stored in secure store
- **Firebase Rules**: Set up proper database rules
- **API Keys**: Never commit sensitive keys to version control
- **SSL/TLS**: All Firebase communications are encrypted

## 🐛 Troubleshooting

### App won't build

```bash
# Clear cache and reinstall
pnpm install --force
rm -rf node_modules
pnpm install
```

### Firebase connection fails

- Verify API key in `lib/firebase.ts`
- Check Firebase project settings
- Ensure internet permission in `app.config.ts`

### Biometric authentication not working

- Ensure device has enrolled biometric data
- Check permissions in `app.config.ts`
- Test on physical device (emulator may not support biometrics)

### News feed not loading

- Check Firebase Realtime Database connection
- Verify database rules allow read access
- Check network connectivity
- Review Firebase console for errors

## 📚 Documentation

- [Expo Documentation](https://docs.expo.dev)
- [React Native Docs](https://reactnative.dev)
- [Firebase Documentation](https://firebase.google.com/docs)
- [NativeWind Documentation](https://www.nativewind.dev)
- [Expo Router Guide](https://docs.expo.dev/routing/introduction/)

## 📝 Build and Deployment Guides

- **BUILD_AND_DEPLOY.md** - Complete build process and signing guide
- **PLAYSTORE_UPLOAD_GUIDE.md** - Step-by-step Play Store upload instructions
- **design.md** - UI/UX design specifications
- **todo.md** - Feature checklist and development tasks

## 🤝 Contributing

To contribute to GenZ Frontier:

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📄 License

GenZ Frontier News App © 2024. All rights reserved.

## 🔗 Links

- **Website**: https://www.genzfrontir.com
- **GitHub**: https://github.com/Sayadbayezid/GenZFrontier
- **Firebase Project**: https://console.firebase.google.com/project/genz-frontier

## 📧 Support

For issues, questions, or feedback:
- Email: support@genzfrontir.com
- GitHub Issues: https://github.com/Sayadbayezid/GenZFrontier/issues

---

**Built with ❤️ for GenZ Frontier**
