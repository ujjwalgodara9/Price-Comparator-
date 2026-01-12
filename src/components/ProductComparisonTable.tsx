import { MatchedProduct, Platform } from '../types/product';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { ExternalLink, Clock } from 'lucide-react';
import { platformNames, platformColors } from '../data/platformData';

interface ProductComparisonTableProps {
  matchedProduct: MatchedProduct;
}

// Helper function to extract numeric value from quantity string (e.g., "5 kg" -> 5)
function extractQuantityValue(quantity: string | undefined): number {
  if (!quantity) return 1;
  const match = quantity.match(/(\d+(?:\.\d+)?)/);
  return match ? parseFloat(match[1]) : 1;
}

// Helper function to calculate price per kg
function calculatePricePerKg(price: number, quantity: string | undefined): number {
  const qty = extractQuantityValue(quantity);
  if (qty === 0) return price;
  return price / qty;
}

export function ProductComparisonTable({ matchedProduct }: ProductComparisonTableProps) {
  const platforms = Object.keys(matchedProduct.platforms || {}) as Platform[];
  if (platforms.length === 0) {
    return null;
  }

  // Convert platform data to array and sort by price (lowest first)
  const platformEntries = platforms.map(platform => ({
    platform,
    ...matchedProduct.platforms[platform]
  }));
  const sortedPlatforms = platformEntries.sort((a, b) => a.price - b.price);
  const cheapestPrice = sortedPlatforms[0].price;

  const productImage = matchedProduct.image || '';
  const productName = matchedProduct.name || '';

  return (
    <Card className="h-full flex flex-col bg-card border">
      <CardContent className="p-4 flex-1 flex flex-col">
        {/* Product Header Section */}
        <div className="mb-4">
          {/* Product Image */}
          <div className="w-full mb-3">
            <div className="aspect-square w-full bg-muted rounded-lg overflow-hidden">
              <img
                src={productImage}
                alt={productName}
                className="w-full h-full object-cover"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = 'https://via.placeholder.com/400?text=No+Image';
                }}
              />
            </div>
          </div>

          {/* Product Info */}
          <div>
            <h3 className="text-lg font-semibold mb-1 line-clamp-2">{productName}</h3>
          </div>
        </div>

        {/* Platform Comparison Table */}
        <div className="space-y-2 flex-1">
          {sortedPlatforms.map((platformData) => {
            const isCheapest = platformData.price === cheapestPrice;
            const platformColor = platformColors[platformData.platform];
            const pricePerKg = calculatePricePerKg(platformData.price, platformData.quantity);
            const quantity = platformData.quantity || '1 pack';

            return (
              <div
                key={platformData.platform}
                className={`p-3 rounded-lg border transition-colors ${
                  isCheapest ? 'bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-800' : 'bg-muted/30'
                }`}
              >
                <div className="flex items-start justify-between gap-2 mb-2">
                  {/* Platform Badge */}
                  <Badge className={platformColor} style={{ fontSize: '0.75rem' }}>
                    {platformNames[platformData.platform]}
                  </Badge>
                  {/* Cheapest Badge */}
                  {isCheapest && (
                    <Badge className="bg-green-500 hover:bg-green-600 text-white" style={{ fontSize: '0.75rem' }}>
                      CHEAPEST
                    </Badge>
                  )}
                </div>

                {/* Quantity */}
                <div className="text-xs text-muted-foreground mb-2">
                  {quantity}
                </div>

                {/* Price */}
                <div className="mb-2">
                  <div className="flex items-center gap-1 flex-wrap">
                    <span className="text-base font-bold">
                      ₹ {platformData.price.toLocaleString()}
                    </span>
                    {platformData.quantity && (
                      <span className="text-xs text-muted-foreground">
                        (₹ {pricePerKg.toFixed(2)}/kg)
                      </span>
                    )}
                  </div>
                </div>

                {/* Delivery Time and Link */}
                <div className="flex items-center justify-between">
                  {platformData.deliveryTime && (
                    <div className="flex items-center gap-1 text-xs text-muted-foreground">
                      <Clock className="h-3 w-3" />
                      <span>{platformData.deliveryTime}</span>
                    </div>
                  )}
                  <a
                    href={platformData.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-muted-foreground hover:text-foreground transition-colors"
                  >
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
