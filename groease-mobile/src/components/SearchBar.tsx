// React Native version of web src/components/SearchBar.tsx
// Changes:
//   - <form> → View + onSubmitEditing on TextInput
//   - <input> → TextInput
//   - <button> → TouchableOpacity
//   - CSS classes → StyleSheet.create()
//   - No lucide-react icons (uses emoji as placeholder)

import React, { useState } from 'react';
import {
  View,
  TextInput,
  TouchableOpacity,
  Text,
  StyleSheet,
} from 'react-native';

interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
}

export function SearchBar({
  onSearch,
  placeholder = 'Search groceries, essentials...',
}: SearchBarProps) {
  const [query, setQuery] = useState('');

  const handleSearch = () => {
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.inputWrapper}>
        <Text style={styles.icon}>🔍</Text>
        <TextInput
          style={styles.input}
          value={query}
          onChangeText={setQuery}
          placeholder={placeholder}
          placeholderTextColor="#93C5FD"
          onSubmitEditing={handleSearch}
          returnKeyType="search"
          autoCorrect={false}
          autoCapitalize="none"
        />
      </View>
      <TouchableOpacity style={styles.button} onPress={handleSearch} activeOpacity={0.8}>
        <Text style={styles.buttonText}>Search</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    gap: 8,
    paddingHorizontal: 16,
    paddingVertical: 10,
  },
  inputWrapper: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    borderWidth: 1.5,
    borderColor: '#BFDBFE',
    paddingHorizontal: 12,
    shadowColor: '#2563EB',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.07,
    shadowRadius: 4,
    elevation: 2,
  },
  icon: {
    fontSize: 16,
    marginRight: 6,
  },
  input: {
    flex: 1,
    height: 46,
    fontSize: 15,
    color: '#1E3A5F',
  },
  button: {
    height: 46,
    paddingHorizontal: 20,
    backgroundColor: '#2563EB',
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#2563EB',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.3,
    shadowRadius: 5,
    elevation: 4,
  },
  buttonText: {
    color: '#FFFFFF',
    fontWeight: '700',
    fontSize: 15,
  },
});
