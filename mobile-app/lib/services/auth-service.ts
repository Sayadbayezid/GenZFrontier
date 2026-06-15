import * as LocalAuthentication from 'expo-local-authentication';
import * as SecureStore from 'expo-secure-store';
import { auth } from '@/lib/firebase';
import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  User,
  onAuthStateChanged,
  Unsubscribe,
} from 'firebase/auth';

export interface AuthUser {
  uid: string;
  email: string | null;
  displayName: string | null;
  photoURL: string | null;
}

class AuthService {
  private currentUser: AuthUser | null = null;
  private biometricEnabled = false;

  /**
   * Initialize biometric authentication
   */
  async initializeBiometric(): Promise<boolean> {
    try {
      const compatible = await LocalAuthentication.hasHardwareAsync();
      if (!compatible) {
        console.log('Device does not support biometric authentication');
        return false;
      }

      const enrolled = await LocalAuthentication.isEnrolledAsync();
      if (!enrolled) {
        console.log('No biometric data enrolled on device');
        return false;
      }

      this.biometricEnabled = true;
      return true;
    } catch (error) {
      console.error('Error initializing biometric:', error);
      return false;
    }
  }

  /**
   * Authenticate with biometric (fingerprint/face)
   */
  async authenticateWithBiometric(): Promise<boolean> {
    try {
      if (!this.biometricEnabled) {
        const initialized = await this.initializeBiometric();
        if (!initialized) {
          return false;
        }
      }

      const result = await LocalAuthentication.authenticateAsync({
        disableDeviceFallback: false,
        fallbackLabel: 'Use passcode',
        reason: 'Authenticate to access GenZ Frontier',
      });

      return result.success;
    } catch (error) {
      console.error('Biometric authentication error:', error);
      return false;
    }
  }

  /**
   * Sign up with email and password
   */
  async signUp(email: string, password: string, displayName: string): Promise<AuthUser | null> {
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;

      // Store user data
      this.currentUser = {
        uid: user.uid,
        email: user.email,
        displayName,
        photoURL: user.photoURL,
      };

      // Optionally save credentials for biometric login
      await this.saveBiometricCredentials(email, password);

      return this.currentUser;
    } catch (error) {
      console.error('Sign up error:', error);
      return null;
    }
  }

  /**
   * Sign in with email and password
   */
  async signIn(email: string, password: string): Promise<AuthUser | null> {
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;

      this.currentUser = {
        uid: user.uid,
        email: user.email,
        displayName: user.displayName,
        photoURL: user.photoURL,
      };

      // Save credentials for biometric login
      await this.saveBiometricCredentials(email, password);

      return this.currentUser;
    } catch (error) {
      console.error('Sign in error:', error);
      return null;
    }
  }

  /**
   * Sign in with biometric
   */
  async signInWithBiometric(): Promise<AuthUser | null> {
    try {
      // First authenticate with biometric
      const authenticated = await this.authenticateWithBiometric();
      if (!authenticated) {
        return null;
      }

      // Retrieve saved credentials
      const credentials = await this.getBiometricCredentials();
      if (!credentials) {
        console.log('No saved credentials found');
        return null;
      }

      // Sign in with saved credentials
      return this.signIn(credentials.email, credentials.password);
    } catch (error) {
      console.error('Biometric sign in error:', error);
      return null;
    }
  }

  /**
   * Save credentials securely for biometric login
   */
  private async saveBiometricCredentials(email: string, password: string): Promise<void> {
    try {
      await SecureStore.setItemAsync('biometric_email', email);
      await SecureStore.setItemAsync('biometric_password', password);
      await SecureStore.setItemAsync('biometric_enabled', 'true');
    } catch (error) {
      console.error('Error saving biometric credentials:', error);
    }
  }

  /**
   * Get saved biometric credentials
   */
  private async getBiometricCredentials(): Promise<{ email: string; password: string } | null> {
    try {
      const email = await SecureStore.getItemAsync('biometric_email');
      const password = await SecureStore.getItemAsync('biometric_password');

      if (!email || !password) {
        return null;
      }

      return { email, password };
    } catch (error) {
      console.error('Error retrieving biometric credentials:', error);
      return null;
    }
  }

  /**
   * Check if biometric login is available
   */
  async isBiometricAvailable(): Promise<boolean> {
    try {
      const credentials = await this.getBiometricCredentials();
      return credentials !== null && this.biometricEnabled;
    } catch (error) {
      return false;
    }
  }

  /**
   * Sign out
   */
  async signOut(): Promise<void> {
    try {
      await signOut(auth);
      this.currentUser = null;
    } catch (error) {
      console.error('Sign out error:', error);
    }
  }

  /**
   * Get current user
   */
  getCurrentUser(): AuthUser | null {
    return this.currentUser;
  }

  /**
   * Subscribe to auth state changes
   */
  subscribeToAuthState(callback: (user: AuthUser | null) => void): Unsubscribe {
    return onAuthStateChanged(auth, (firebaseUser) => {
      if (firebaseUser) {
        this.currentUser = {
          uid: firebaseUser.uid,
          email: firebaseUser.email,
          displayName: firebaseUser.displayName,
          photoURL: firebaseUser.photoURL,
        };
      } else {
        this.currentUser = null;
      }
      callback(this.currentUser);
    });
  }

  /**
   * Clear biometric credentials
   */
  async clearBiometricCredentials(): Promise<void> {
    try {
      await SecureStore.deleteItemAsync('biometric_email');
      await SecureStore.deleteItemAsync('biometric_password');
      await SecureStore.deleteItemAsync('biometric_enabled');
    } catch (error) {
      console.error('Error clearing biometric credentials:', error);
    }
  }
}

export const authService = new AuthService();
