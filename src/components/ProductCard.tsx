import { Product } from '../types/product';
import { Card, CardContent, CardFooter, CardHeader } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Star, ExternalLink } from 'lucide-react';
import { platformNames, platformColors } from '../data/platformData';

interface ProductCardProps {
  product: Product;
}

export function ProductCard({ product }: ProductCardProps) {
  const platformColor = platformColors[product.platform];

  return (
    <Card className="h-full flex flex-col hover:shadow-lg transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <Badge className={platformColor}>{platformNames[product.platform]}</Badge>
          {!product.availability && (
            <Badge variant="destructive">Out of Stock</Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="flex-1 space-y-4">
        <div className="aspect-square w-full bg-muted rounded-lg overflow-hidden">
          <img
            src={product.image}
            alt={product.name}
            className="w-full h-full object-cover"
            onError={(e) => {
              (e.target as HTMLImageElement).src = 'https://via.placeholder.com/400?text=No+Image';
            }}
          />
        </div>
        <div>
          <h3 className="font-semibold text-lg line-clamp-2 mb-2">{product.name}</h3>
          <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
            {product.description}
          </p>
          <div className="flex items-center gap-2 mb-2">
            <div className="flex items-center gap-1">
              <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
              <span className="text-sm font-medium">{product.rating}</span>
            </div>
            <span className="text-sm text-muted-foreground">
              ({product.reviewCount.toLocaleString()} reviews)
            </span>
          </div>
          <div className="flex flex-wrap gap-1 mb-3">
            {product.features.slice(0, 2).map((feature, idx) => (
              <Badge key={idx} variant="outline" className="text-xs">
                {feature}
              </Badge>
            ))}
          </div>
        </div>
      </CardContent>
      <CardFooter className="flex-col gap-2 pt-4">
        <div className="w-full">
          <div className="text-2xl font-bold">
            {product.currency} {product.price.toLocaleString()}
          </div>
        </div>
        <Button className="w-full" variant="default" asChild>
          <a href={product.link} target="_blank" rel="noopener noreferrer">
            View on {platformNames[product.platform]}
            <ExternalLink className="ml-2 h-4 w-4" />
          </a>
        </Button>
      </CardFooter>
    </Card>
  );
}

