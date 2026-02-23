// React Native version of web src/components/LocationPopup.tsx
// Changes:
//   - Fixed overlay <div> → Modal component (slides up from bottom)
//   - <input> → TextInput
//   - onClick dropdown → FlatList
//   - CSS → StyleSheet
//   - KeyboardAvoidingView handles keyboard pushing content up on both iOS and Android
// Logic (debounced autocomplete, suggestion selection) is identical

import React, { useState, useEffect, useRef } from 'react';
import {
  Modal,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  ActivityIndicator,
  StyleSheet,
  KeyboardAvoidingView,
  Platform as RNPlatform,
  ScrollView,
} from 'react-native';
import { fetchAutocomplete, type GeoapifyResult } from '../services/geoapifyService';

interface LocationModalProps {
  visible: boolean;
  onSelect: (location: {
    address: string;
    lat: number;
    lng: number;
    city?: string;
    state?: string;
    country?: string;
  }) => void;
  onClose?: () => void;
}

export function LocationModal({ visible, onSelect, onClose }: LocationModalProps) {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<GeoapifyResult[]>([]);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<TextInput>(null);

  // Debounced autocomplete — identical logic to web LocationPopup
  useEffect(() => {
    if (!query.trim()) {
      setSuggestions([]);
      return;
    }

    const delay = setTimeout(() => {
      setLoading(true);
      fetchAutocomplete(query)
        .then(setSuggestions)
        .catch(err => {
          console.warn('[LocationModal] Autocomplete error:', err);
          setSuggestions([]);
        })
        .finally(() => setLoading(false));
    }, 400);

    return () => clearTimeout(delay);
  }, [query]);

  const handleSelect = (result: GeoapifyResult) => {
    const lat = result.lat ?? 0;
    const lon = result.lon ?? 0;
    const address =
      result.formatted ||
      [result.address_line1, result.address_line2].filter(Boolean).join(', ') ||
      `${result.city || ''}, ${result.state || ''}`.trim() ||
      'Unknown';

    onSelect({
      address,
      lat,
      lng: lon,
      city: result.city,
      state: result.state,
      country: result.country,
    });

    setQuery('');
    setSuggestions([]);
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent
      statusBarTranslucent
      onShow={() => {
        // Focus input after modal animation completes
        setTimeout(() => inputRef.current?.focus(), 300);
      }}
    >
      {/* Dimmed backdrop — tap outside does nothing since location is required */}
      <KeyboardAvoidingView
        style={styles.overlay}
        behavior={RNPlatform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={0}
      >
        <View style={styles.sheet}>
          {/* Blue header */}
          <View style={styles.header}>
            <View style={styles.headerRow}>
              <View style={{ flex: 1 }}>
                <Text style={styles.title}>Set Your Location</Text>
                <Text style={styles.subtitle}>
                  Provide your delivery location to see products
                </Text>
              </View>
              {onClose && (
                <TouchableOpacity onPress={onClose} style={styles.closeBtn} activeOpacity={0.7}>
                  <Text style={styles.closeBtnText}>✕</Text>
                </TouchableOpacity>
              )}
            </View>
          </View>

          {/* Search input */}
          <View style={styles.inputWrapper}>
            <TextInput
              ref={inputRef}
              style={styles.input}
              value={query}
              onChangeText={setQuery}
              placeholder="Search delivery location"
              placeholderTextColor="#93C5FD"
              autoCorrect={false}
              autoCapitalize="none"
              returnKeyType="search"
            />
            {loading && (
              <ActivityIndicator
                style={styles.spinner}
                size="small"
                color="#2563EB"
              />
            )}
          </View>

          {/* Location suggestions — ScrollView so it doesn't fight keyboard */}
          <FlatList
            data={suggestions}
            keyExtractor={(item, idx) => `${item.lat}-${item.lon}-${idx}`}
            keyboardShouldPersistTaps="always"
            keyboardDismissMode="none"
            style={styles.list}
            contentContainerStyle={styles.listContent}
            renderItem={({ item }) => (
              <TouchableOpacity
                style={styles.suggestionItem}
                onPress={() => handleSelect(item)}
                activeOpacity={0.7}
              >
                <Text style={styles.suggestionMain}>
                  {item.address_line1 || item.city || item.formatted || 'Address'}
                </Text>
                <Text style={styles.suggestionSub}>
                  {[item.city, item.state, item.country].filter(Boolean).join(', ') ||
                    item.formatted}
                </Text>
              </TouchableOpacity>
            )}
            ListEmptyComponent={
              !loading && query.trim().length > 0 ? (
                <Text style={styles.emptyText}>No results found</Text>
              ) : null
            }
          />
        </View>
      </KeyboardAvoidingView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  sheet: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    // Use flex instead of maxHeight so KeyboardAvoidingView can shrink it
    maxHeight: '90%',
    paddingBottom: RNPlatform.OS === 'android' ? 16 : 32,
    overflow: 'hidden',
  },
  header: {
    backgroundColor: '#2563EB',
    paddingHorizontal: 20,
    paddingTop: 24,
    paddingBottom: 20,
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  closeBtn: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: 'rgba(255,255,255,0.2)',
    alignItems: 'center',
    justifyContent: 'center',
    marginLeft: 8,
    marginTop: 2,
  },
  closeBtnText: {
    fontSize: 16,
    color: '#FFFFFF',
    fontWeight: '700',
  },
  title: {
    fontSize: 20,
    fontWeight: '800',
    color: '#FFFFFF',
  },
  subtitle: {
    fontSize: 13,
    color: '#BFDBFE',
    marginTop: 4,
  },
  inputWrapper: {
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: 8,
  },
  input: {
    height: 48,
    borderWidth: 2,
    borderColor: '#BFDBFE',
    borderRadius: 10,
    paddingHorizontal: 16,
    fontSize: 15,
    color: '#111827',
    backgroundColor: '#F8FAFF',
  },
  spinner: {
    position: 'absolute',
    right: 32,
    top: 32,
  },
  list: {
    flexGrow: 0,
    paddingHorizontal: 20,
    maxHeight: 300,
  },
  listContent: {
    paddingBottom: 8,
  },
  suggestionItem: {
    paddingVertical: 14,
    borderBottomWidth: 1,
    borderBottomColor: '#EFF6FF',
  },
  suggestionMain: {
    fontSize: 14,
    fontWeight: '600',
    color: '#111827',
  },
  suggestionSub: {
    fontSize: 12,
    color: '#2563EB',
    marginTop: 2,
  },
  emptyText: {
    textAlign: 'center',
    color: '#9CA3AF',
    fontSize: 14,
    paddingVertical: 20,
  },
});
