import { LocationData } from '../types/product';
import { MapPin } from 'lucide-react';
import { Badge } from './ui/badge';

interface LocationDisplayProps {
  location: LocationData;
  onRefresh?: () => void;
}

export function LocationDisplay({ location, onRefresh }: LocationDisplayProps) {
  return (
    <div className="flex items-center gap-2">
      <MapPin className="h-4 w-4 text-muted-foreground" />
      <Badge variant="outline" className="text-sm">
        {location.city}, {location.state}
      </Badge>
      {onRefresh && (
        <button
          onClick={onRefresh}
          className="text-xs text-primary hover:underline"
        >
          Change
        </button>
      )}
    </div>
  );
}

