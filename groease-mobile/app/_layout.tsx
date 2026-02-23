// Expo Router root layout — sets up the navigation stack for all screens

import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';

export default function RootLayout() {
  return (
    <>
      <StatusBar style="light" backgroundColor="#1D4ED8" />
      <Stack
        screenOptions={{
          headerStyle: { backgroundColor: '#1D4ED8' },
          headerTintColor: '#FFFFFF',
          headerTitleStyle: { fontWeight: '800', fontSize: 17 },
          contentStyle: { backgroundColor: '#F0F9FF' },
        }}
      >
        {/* Home screen — header hidden, custom header inside the screen */}
        <Stack.Screen name="index" options={{ headerShown: false }} />

        {/* Results screen — shows query in title, back button auto-added */}
        <Stack.Screen
          name="results"
          options={{
            title: 'Compare Prices',
            headerBackTitle: 'Home',
          }}
        />
      </Stack>
    </>
  );
}
