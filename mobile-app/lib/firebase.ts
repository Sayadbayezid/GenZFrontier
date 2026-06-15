import { initializeApp } from 'firebase/app';
import { getAuth, connectAuthEmulator } from 'firebase/auth';
import { getDatabase, connectDatabaseEmulator } from 'firebase/database';
import { getStorage, connectStorageEmulator } from 'firebase/storage';

// Firebase configuration from google-services.json
const firebaseConfig = {
  apiKey: 'apikeygenzfrontier',
  authDomain: 'genz-frontier.firebaseapp.com',
  projectId: 'genz-frontier',
  storageBucket: 'genz-frontier.firebasestorage.app',
  messagingSenderId: '967263604043',
  appId: '1:967263604043:android:09e3e1e0e62eb6e7e86cce',
  databaseURL: 'https://genz-frontier-default-rtdb.firebaseio.com',
};

// Initialize Firebase
export const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication
export const auth = getAuth(app);

// Initialize Firebase Realtime Database
export const database = getDatabase(app);

// Initialize Firebase Storage
export const storage = getStorage(app);

// Optional: Connect to emulators for development
// Uncomment these lines if you're running Firebase emulators locally
/*
if (__DEV__) {
  try {
    connectAuthEmulator(auth, 'http://localhost:9099', { disableWarnings: true });
    connectDatabaseEmulator(database, 'localhost', 9000);
    connectStorageEmulator(storage, 'localhost', 9199);
  } catch (error) {
    // Emulators already connected
  }
}
*/

export default app;
