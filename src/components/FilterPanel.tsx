import { ComparisonFilters, Platform } from '../types/product';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Checkbox } from './ui/checkbox';
import { Select } from './ui/select';
import { Input } from './ui/input';
import { platformNames } from '../data/mockProducts';

interface FilterPanelProps {
  filters: ComparisonFilters;
  onFiltersChange: (filters: ComparisonFilters) => void;
}

const allPlatforms: Platform[] = ['amazon', 'flipkart', 'myntra', 'nykaa', 'meesho', 'ajio', 'snapdeal', 'tatacliq'];

export function FilterPanel({ filters, onFiltersChange }: FilterPanelProps) {
  const handlePlatformToggle = (platform: Platform) => {
    const newPlatforms = filters.platforms.includes(platform)
      ? filters.platforms.filter(p => p !== platform)
      : [...filters.platforms, platform];
    
    onFiltersChange({ ...filters, platforms: newPlatforms });
  };

  const handleSelectAll = () => {
    onFiltersChange({ ...filters, platforms: allPlatforms });
  };

  const handleClearAll = () => {
    onFiltersChange({ ...filters, platforms: [] });
  };

  return (
    <Card className="sticky top-4">
      <CardHeader>
        <CardTitle>Filters</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Platforms */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="text-sm font-medium">Platforms</label>
            <div className="flex gap-2">
              <button
                onClick={handleSelectAll}
                className="text-xs text-primary hover:underline"
              >
                All
              </button>
              <button
                onClick={handleClearAll}
                className="text-xs text-muted-foreground hover:underline"
              >
                Clear
              </button>
            </div>
          </div>
          <div className="space-y-2">
            {allPlatforms.map(platform => (
              <label
                key={platform}
                className="flex items-center space-x-2 cursor-pointer"
              >
                <Checkbox
                  checked={filters.platforms.includes(platform)}
                  onChange={() => handlePlatformToggle(platform)}
                />
                <span className="text-sm">{platformNames[platform]}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Price Range */}
        <div>
          <label className="text-sm font-medium mb-2 block">Price Range</label>
          <div className="flex gap-2">
            <Input
              type="number"
              placeholder="Min"
              value={filters.minPrice || ''}
              onChange={(e) =>
                onFiltersChange({
                  ...filters,
                  minPrice: e.target.value ? Number(e.target.value) : undefined,
                })
              }
            />
            <Input
              type="number"
              placeholder="Max"
              value={filters.maxPrice || ''}
              onChange={(e) =>
                onFiltersChange({
                  ...filters,
                  maxPrice: e.target.value ? Number(e.target.value) : undefined,
                })
              }
            />
          </div>
        </div>

        {/* Rating */}
        <div>
          <label className="text-sm font-medium mb-2 block">Minimum Rating</label>
          <Select
            value={filters.minRating || ''}
            onChange={(e) =>
              onFiltersChange({
                ...filters,
                minRating: e.target.value ? Number(e.target.value) : undefined,
              })
            }
          >
            <option value="">Any</option>
            <option value="4.5">4.5+ ⭐</option>
            <option value="4.0">4.0+ ⭐</option>
            <option value="3.5">3.5+ ⭐</option>
            <option value="3.0">3.0+ ⭐</option>
          </Select>
        </div>

        {/* Sort By */}
        <div>
          <label className="text-sm font-medium mb-2 block">Sort By</label>
          <Select
            value={filters.sortBy}
            onChange={(e) =>
              onFiltersChange({
                ...filters,
                sortBy: e.target.value as ComparisonFilters['sortBy'],
              })
            }
          >
            <option value="price-low">Price: Low to High</option>
            <option value="price-high">Price: High to Low</option>
            <option value="rating">Highest Rated</option>
            <option value="reviews">Most Reviews</option>
          </Select>
        </div>
      </CardContent>
    </Card>
  );
}

