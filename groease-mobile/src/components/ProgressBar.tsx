// React Native animated progress bar
// Replicates the same eased progress animation as App.tsx in the web version
// Uses Animated API instead of CSS transitions

import React, { useEffect, useRef } from 'react';
import { View, Text, Animated, StyleSheet } from 'react-native';

interface ProgressBarProps {
  progress: number; // 0–100
  label?: string;
}

export function ProgressBar({ progress, label = 'Searching platforms...' }: ProgressBarProps) {
  const animatedValue = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(animatedValue, {
      toValue: progress,
      duration: 300,
      useNativeDriver: false,
    }).start();
  }, [progress]);

  const widthPercent = animatedValue.interpolate({
    inputRange: [0, 100],
    outputRange: ['0%', '100%'],
  });

  return (
    <View style={styles.container}>
      <View style={styles.labelRow}>
        <Text style={styles.label}>{label}</Text>
        <Text style={styles.percent}>{Math.round(progress)}%</Text>
      </View>
      <View style={styles.track}>
        <Animated.View style={[styles.fill, { width: widthPercent }]} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 16,
    paddingVertical: 14,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#DBEAFE',
  },
  labelRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#065F46',
  },
  percent: {
    fontSize: 13,
    fontWeight: '600',
    color: '#059669',
  },
  track: {
    height: 8,
    backgroundColor: '#D1FAE5',
    borderRadius: 4,
    overflow: 'hidden',
  },
  fill: {
    height: '100%',
    backgroundColor: '#059669',
    borderRadius: 4,
  },
});
