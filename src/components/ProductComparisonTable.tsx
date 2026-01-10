import { Product } from '../types/product';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { ExternalLink, Clock } from 'lucide-react';
import { platformNames, platformColors } from '../data/platformData';

interface ProductComparisonTableProps {
  products: Product[];
  productName: string;
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

export function ProductComparisonTable({ products, productName }: ProductComparisonTableProps) {
  if (products.length === 0) {
    return null;
  }

  // Sort products by price (lowest first)
  const sortedProducts = [...products].sort((a, b) => a.price - b.price);
  const cheapestProduct = sortedProducts[0];
  const cheapestPrice = cheapestProduct.price;

  // Get the first product's image (they should all be the same product)
  const productImage = products[0]?.image || '';
  const productDescription = products[0]?.description || '';

  return (
    <Card className="mb-8 bg-card border">
      <CardContent className="p-6">
        {/* Product Header Section */}
        <div className="flex items-start gap-6 mb-6 pb-6 border-b">
          {/* Product Image */}
          <div className="flex-shrink-0">
            <div className="w-32 h-32 bg-muted rounded-lg overflow-hidden">
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
          <div className="flex-1">
            <h3 className="text-xl font-semibold mb-2">{productName}</h3>
            {productDescription && (
              <p className="text-sm text-muted-foreground line-clamp-2">{productDescription}</p>
            )}
          </div>
        </div>

        {/* Platform Comparison Table */}
        <div className="space-y-3">
          {sortedProducts.map((product) => {
            const isCheapest = product.price === cheapestPrice;
            const platformColor = platformColors[product.platform];
            const pricePerKg = calculatePricePerKg(product.price, product.quantity);
            const quantity = product.quantity || '1 pack';

            return (
              <div
                key={product.id}
                className={`flex items-center gap-4 p-4 rounded-lg border transition-colors ${
                  isCheapest ? 'bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-800' : 'bg-muted/30'
                }`}
              >
                {/* Platform Badge */}
                <div className="flex-shrink-0">
                  <Badge className={platformColor} style={{ minWidth: '80px', justifyContent: 'center' }}>
                    {platformNames[product.platform]}
                  </Badge>
                </div>

                {/* Quantity */}
                <div className="flex-shrink-0 min-w-[120px]">
                  <div className="text-sm font-medium">{quantity}</div>
                </div>

                {/* Price */}
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-lg font-bold">
                      {product.currency} {product.price.toLocaleString()}
                    </span>
                    {product.quantity && (
                      <span className="text-sm text-muted-foreground">
                        ({product.currency} {pricePerKg.toFixed(2)}/kg)
                      </span>
                    )}
                    <a
                      href={product.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-muted-foreground hover:text-foreground transition-colors"
                    >
                      <ExternalLink className="h-4 w-4" />
                    </a>
                  </div>
                </div>

                {/* Delivery Time */}
                {product.deliveryTime && (
                  <div className="flex-shrink-0 flex items-center gap-1 text-sm text-muted-foreground min-w-[100px]">
                    <Clock className="h-4 w-4" />
                    <span>{product.deliveryTime}</span>
                  </div>
                )}

                {/* Cheapest Badge */}
                {isCheapest && (
                  <div className="flex-shrink-0">
                    <Badge className="bg-green-500 hover:bg-green-600 text-white">
                      CHEAPEST
                    </Badge>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
