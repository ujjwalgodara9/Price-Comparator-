import { LocationData } from '../types/product';
import { MapPin } from 'lucide-react';
import { Badge } from './ui/badge';

interface LocationDisplayProps {
  location: LocationData;
  onRefresh?: () => void;
}

export function LocationDisplay({ location, onRefresh }: LocationDisplayProps) {
  return (
    <div className="flex items-center gap-3">
      <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-50 rounded-lg border border-blue-200">
        <MapPin className="h-4 w-4 text-blue-600" />
        <span className="text-sm font-medium text-gray-700">
          {location.city}, {location.state}
        </span>
      </div>
      {onRefresh && (
        <button
          onClick={onRefresh}
          className="text-xs text-blue-600 hover:text-blue-700 font-medium hover:underline transition-colors"
        >
          Change
        </button>
      )}
    </div>
  );
}

