import { MatchedProduct, Platform } from '../types/product';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { ExternalLink, Clock } from 'lucide-react';
import { platformNames, platformColors } from '../data/platformData';

interface ProductComparisonTableProps {
  matchedProduct: MatchedProduct;
}


export function ProductComparisonTable({ matchedProduct }: ProductComparisonTableProps) {
  const platforms = Object.keys(matchedProduct.platforms || {}) as Platform[];
  
  // Debug: Log platform data
  console.log('[ProductComparisonTable] Rendering product:', {
    name: matchedProduct.name,
    platforms: platforms,
    platformCount: platforms.length,
    platformData: matchedProduct.platforms
  });
  
  if (platforms.length === 0) {
    console.warn('[ProductComparisonTable] No platforms found for product:', matchedProduct.name);
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
    <Card className="h-full flex flex-col bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-lg hover:border-blue-200 transition-all duration-300 overflow-hidden group">
      <CardContent className="p-5 flex-1 flex flex-col">
        {/* Product Header Section */}
        <div className="mb-5">
          {/* Product Image */}
          <div className="w-full mb-4">
            <div className="aspect-square w-full bg-gradient-to-br from-gray-100 to-gray-200 rounded-lg overflow-hidden border border-gray-200 shadow-inner group-hover:shadow-md transition-shadow">
              <img
                src={productImage}
                alt={productName}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = 'https://via.placeholder.com/400?text=No+Image';
                }}
              />
            </div>
          </div>

          {/* Product Info */}
          <div>
            <h3 className="text-base font-semibold text-gray-900 mb-1 line-clamp-2 leading-snug">{productName}</h3>
          </div>
        </div>

        {/* Platform Comparison Table */}
        <div className="flex-1">
          {sortedPlatforms.length > 1 && (
            <div className="text-xs text-blue-600 font-semibold mb-4 px-3 py-1.5 bg-blue-50 rounded-md border border-blue-200 text-center">
              {sortedPlatforms.length} platforms compared
            </div>
          )}
          <div className="space-y-3">
            {sortedPlatforms.map((platformData, index) => {
              const isCheapest = platformData.price === cheapestPrice;
              const platformColor = platformColors[platformData.platform];
              const quantity = platformData.quantity || '1 pack';

              return (
                <div
                  key={`${platformData.platform}-${index}`}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    isCheapest 
                      ? 'bg-gradient-to-br from-green-50 to-emerald-50 border-green-300 shadow-md hover:shadow-lg ring-2 ring-green-200' 
                      : 'bg-gradient-to-br from-gray-50 to-gray-100 border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2 mb-3">
                    {/* Platform Badge */}
                    <Badge 
                      className={`${platformColor} text-xs font-semibold px-2.5 py-1 rounded-md`}
                    >
                      {platformNames[platformData.platform]}
                    </Badge>
                    {/* Cheapest Badge */}
                    {isCheapest && (
                      <Badge className="bg-green-600 hover:bg-green-700 text-white text-xs font-semibold px-2.5 py-1 rounded-md shadow-sm">
                        BEST PRICE
                      </Badge>
                    )}
                  </div>

                  {/* Quantity */}
                  <div className="text-xs text-gray-500 mb-3 font-medium">
                    {quantity}
                  </div>

                  {/* Price */}
                  <div className="mb-3">
                    <div className="flex items-baseline gap-1">
                      <span className="text-2xl font-bold text-gray-900">
                        ₹{platformData.price.toLocaleString()}
                      </span>
                    </div>
                  </div>

                  {/* Delivery Time and Link */}
                  <div className="flex items-center justify-between pt-2 border-t border-gray-200">
                    {platformData.deliveryTime && (
                      <div className="flex items-center gap-1.5 text-xs text-gray-600">
                        <Clock className="h-3.5 w-3.5 text-gray-400" />
                        <span className="font-medium">{platformData.deliveryTime}</span>
                      </div>
                    )}
                    <a
                      href={platformData.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-semibold rounded-md transition-colors border border-blue-200"
                    >
                      <span>View</span>
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
