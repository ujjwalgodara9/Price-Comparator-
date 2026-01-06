import { Product } from '../types/product';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Star, ExternalLink, TrendingDown, TrendingUp } from 'lucide-react';
import { platformNames, platformColors } from '../data/mockProducts';

interface ProductComparisonTableProps {
  products: Product[];
  productName: string;
}

export function ProductComparisonTable({ products, productName }: ProductComparisonTableProps) {
  if (products.length === 0) {
    return null;
  }

  const sortedProducts = [...products].sort((a, b) => a.price - b.price);
  const lowestPrice = sortedProducts[0].price;
  const highestPrice = sortedProducts[sortedProducts.length - 1].price;

  const getPriceDifference = (price: number) => {
    const diff = price - lowestPrice;
    const percent = ((diff / lowestPrice) * 100).toFixed(1);
    return { diff, percent };
  };

  return (
    <Card className="mb-8">
      <CardHeader>
        <CardTitle className="text-xl">{productName}</CardTitle>
        <p className="text-sm text-muted-foreground">
          Compare prices across {products.length} platform{products.length !== 1 ? 's' : ''}
        </p>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {sortedProducts.map((product) => {
              const { diff, percent } = getPriceDifference(product.price);
              const isLowest = product.price === lowestPrice;
              const platformColor = platformColors[product.platform];

              return (
                <div
                  key={product.id}
                  className={`border rounded-lg p-4 ${
                    isLowest ? 'ring-2 ring-green-500 bg-green-50 dark:bg-green-950' : ''
                  }`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <Badge className={platformColor}>
                      {platformNames[product.platform]}
                    </Badge>
                    {isLowest && (
                      <Badge variant="default" className="bg-green-500">
                        Best Price
                      </Badge>
                    )}
                  </div>

                  <div className="aspect-square w-full bg-muted rounded-lg overflow-hidden mb-3">
                    <img
                      src={product.image}
                      alt={product.name}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        (e.target as HTMLImageElement).src = 'https://via.placeholder.com/400?text=No+Image';
                      }}
                    />
                  </div>

                  <div className="space-y-2 mb-3">
                    <div className="flex items-center gap-2">
                      <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                      <span className="text-sm font-medium">{product.rating}</span>
                      <span className="text-xs text-muted-foreground">
                        ({product.reviewCount.toLocaleString()})
                      </span>
                    </div>
                    {!product.availability && (
                      <Badge variant="destructive" className="text-xs">
                        Out of Stock
                      </Badge>
                    )}
                  </div>

                  <div className="mb-3">
                    <div className="text-2xl font-bold mb-1">
                      {product.currency} {product.price.toLocaleString()}
                    </div>
                    {!isLowest && diff > 0 && (
                      <div className="flex items-center gap-1 text-sm text-red-600">
                        <TrendingUp className="h-3 w-3" />
                        <span>{product.currency} {diff.toLocaleString()} ({percent}%) more</span>
                      </div>
                    )}
                    {isLowest && (
                      <div className="flex items-center gap-1 text-sm text-green-600">
                        <TrendingDown className="h-3 w-3" />
                        <span>Lowest price</span>
                      </div>
                    )}
                  </div>

                  <Button
                    className="w-full"
                    variant={isLowest ? 'default' : 'outline'}
                    asChild
                  >
                    <a href={product.link} target="_blank" rel="noopener noreferrer">
                      Buy Now
                      <ExternalLink className="ml-2 h-4 w-4" />
                    </a>
                  </Button>
                </div>
              );
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

