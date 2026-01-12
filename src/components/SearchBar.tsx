import { useState } from 'react';
import { Search } from 'lucide-react';
import { Input } from './ui/input';
import { Button } from './ui/button';

interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
}

export function SearchBar({ onSearch, placeholder = "Search for groceries, essentials, and more..." }: SearchBarProps) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('[SearchBar] Form submitted with query:', query);
    if (query.trim()) {
      onSearch(query);
    } else {
      console.log('[SearchBar] Empty query, not searching');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-3xl mx-auto">
      <div className="flex gap-3">
        <div className="relative flex-1">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-green-500/10 rounded-lg blur-sm"></div>
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5 z-10" />
            <Input
              type="text"
              placeholder={placeholder}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="pl-12 pr-4 py-3 h-12 text-base border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 bg-white rounded-lg shadow-md hover:shadow-lg transition-all"
            />
          </div>
        </div>
        <Button 
          type="submit"
          className="px-8 h-12 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white font-semibold rounded-lg shadow-md hover:shadow-lg transition-all focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transform hover:scale-105"
        >
          Search
        </Button>
      </div>
    </form>
  );
}

