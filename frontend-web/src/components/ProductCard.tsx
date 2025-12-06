import React, { useState } from 'react';
import {
  Card,
  CardMedia,
  CardContent,
  CardActions,
  Typography,
  Button,
  Box,
  Chip,
  IconButton,
  Skeleton,
  Fade,
  useTheme,
} from '@mui/material';
import {
  Add as AddIcon,
  Favorite as FavoriteIcon,
  FavoriteBorder as FavoriteBorderIcon,
  ShoppingCart as CartIcon,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';

const StyledCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  transition: 'all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1)',
  cursor: 'pointer',
  overflow: 'hidden',
  borderRadius: theme.spacing(2),
  boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
  border: '1px solid rgba(139, 195, 74, 0.08)',
  
  '&:hover': {
    transform: 'translateY(-8px)',
    boxShadow: '0 12px 40px rgba(139, 195, 74, 0.15)',
    
    '& .product-image': {
      transform: 'scale(1.05)',
    },
    
    '& .product-overlay': {
      opacity: 1,
    },
    
    '& .add-to-cart': {
      transform: 'translateY(0)',
      opacity: 1,
    },
  },
}));

const ProductImageContainer = styled(Box)({
  position: 'relative',
  height: 240,
  overflow: 'hidden',
});

const ProductImage = styled(CardMedia)({
  height: '100%',
  transition: 'transform 0.4s ease',
  backgroundColor: '#f8f9fa',
});

const ProductOverlay = styled(Box)({
  position: 'absolute',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  background: 'linear-gradient(135deg, rgba(139, 195, 74, 0.1) 0%, rgba(76, 175, 80, 0.1) 100%)',
  opacity: 0,
  transition: 'opacity 0.3s ease',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
});

const QuickActionButton = styled(IconButton)(({ theme }) => ({
  backgroundColor: 'rgba(255, 255, 255, 0.9)',
  backdropFilter: 'blur(10px)',
  border: '1px solid rgba(139, 195, 74, 0.2)',
  margin: theme.spacing(0.5),
  transition: 'all 0.2s ease',
  
  '&:hover': {
    backgroundColor: '#8BC34A',
    color: 'white',
    transform: 'scale(1.1)',
  },
}));

const StyledCardContent = styled(CardContent)(({ theme }) => ({
  flexGrow: 1,
  padding: theme.spacing(2, 2.5),
  
  '&:last-child': {
    paddingBottom: theme.spacing(2),
  },
}));

const PriceBox = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1),
  marginTop: theme.spacing(1),
}));

const Price = styled(Typography)(({ theme }) => ({
  fontWeight: 600,
  color: '#2E7D32',
  fontSize: '1.25rem',
  fontFamily: "'Playfair Display', serif",
}));

const StockChip = styled(Chip)(({ inStock }: { inStock: boolean }) => ({
  fontWeight: 500,
  fontSize: '0.75rem',
  height: 24,
  backgroundColor: inStock ? 'rgba(139, 195, 74, 0.1)' : 'rgba(244, 67, 54, 0.1)',
  color: inStock ? '#2E7D32' : '#C62828',
  border: `1px solid ${inStock ? 'rgba(139, 195, 74, 0.3)' : 'rgba(244, 67, 54, 0.3)'}`,
}));

const AddToCartButton = styled(Button)(({ theme }) => ({
  margin: theme.spacing(1, 2.5, 2),
  borderRadius: theme.spacing(3),
  textTransform: 'none',
  fontWeight: 600,
  padding: theme.spacing(1, 3),
  background: 'linear-gradient(135deg, #8BC34A 0%, #4CAF50 100%)',
  color: 'white',
  border: 'none',
  transform: 'translateY(10px)',
  opacity: 0,
  transition: 'all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1)',
  
  '&:hover': {
    background: 'linear-gradient(135deg, #7CB342 0%, #43A047 100%)',
    transform: 'translateY(0) scale(1.02)',
    boxShadow: '0 6px 20px rgba(139, 195, 74, 0.3)',
  },
  
  '&:disabled': {
    background: 'rgba(0,0,0,0.12)',
    color: 'rgba(0,0,0,0.26)',
    transform: 'translateY(10px)',
    opacity: 0.6,
  },
}));

interface Product {
  id: number;
  name: string;
  description?: string | null;
  price: number;
  inventory_count: number;
  image_url?: string | null;
}

interface ProductCardProps {
  product: Product;
  onAddToCart: (product: Product) => void;
  loading?: boolean;
}

const ProductCard: React.FC<ProductCardProps> = ({ 
  product, 
  onAddToCart, 
  loading = false 
}) => {
  const [favorite, setFavorite] = useState(false);
  const [imageLoading, setImageLoading] = useState(true);
  const theme = useTheme();

  const isInStock = product.inventory_count > 0;
  const isLowStock = product.inventory_count <= 5 && product.inventory_count > 0;

  const handleAddToCart = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (isInStock) {
      onAddToCart(product);
    }
  };

  const handleFavoriteToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    setFavorite(!favorite);
  };

  if (loading) {
    return (
      <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Skeleton variant="rectangular" height={240} />
        <CardContent sx={{ flexGrow: 1 }}>
          <Skeleton variant="text" height={32} width="80%" />
          <Skeleton variant="text" height={20} width="60%" sx={{ mt: 1 }} />
          <Skeleton variant="text" height={28} width="40%" sx={{ mt: 2 }} />
        </CardContent>
        <CardActions>
          <Skeleton variant="rectangular" height={36} width="100%" sx={{ mx: 2, mb: 2 }} />
        </CardActions>
      </Card>
    );
  }

  return (
    <StyledCard>
      <ProductImageContainer>
        <ProductImage
          className="product-image"
          image={product.image_url || '/api/placeholder/300/240'}
          title={product.name}
          onLoad={() => setImageLoading(false)}
        />
        
        {imageLoading && (
          <Skeleton 
            variant="rectangular" 
            width="100%" 
            height="100%" 
            sx={{ position: 'absolute', top: 0, left: 0 }}
          />
        )}
        
        <ProductOverlay className="product-overlay">
          <QuickActionButton
            size="small"
            onClick={handleFavoriteToggle}
            aria-label="Add to favorites"
          >
            {favorite ? <FavoriteIcon /> : <FavoriteBorderIcon />}
          </QuickActionButton>
        </ProductOverlay>
        
        <Box sx={{ position: 'absolute', top: 12, right: 12 }}>
          {isLowStock && isInStock && (
            <StockChip
              label="Low Stock"
              size="small"
              inStock={false}
            />
          )}
          {!isInStock && (
            <StockChip
              label="Out of Stock"
              size="small"
              inStock={false}
            />
          )}
        </Box>
      </ProductImageContainer>

      <StyledCardContent>
        <Typography
          variant="h6"
          component="h3"
          sx={{
            fontWeight: 600,
            lineHeight: 1.3,
            color: '#1B5E20',
            fontFamily: "'Playfair Display', serif",
            fontSize: '1.1rem',
          }}
        >
          {product.name}
        </Typography>
        
        {product.description && (
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{
              mt: 0.5,
              lineHeight: 1.4,
              fontFamily: "'Inter', sans-serif",
              fontSize: '0.875rem',
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
            }}
          >
            {product.description}
          </Typography>
        )}
        
        <PriceBox>
          <Price variant="h6">
            ${Number(product.price).toFixed(2)}
          </Price>
          {isInStock && (
            <StockChip
              label={`${product.inventory_count} available`}
              size="small"
              inStock={true}
            />
          )}
        </PriceBox>
      </StyledCardContent>

      <AddToCartButton
        className="add-to-cart"
        variant="contained"
        startIcon={<CartIcon />}
        onClick={handleAddToCart}
        disabled={!isInStock}
        fullWidth={false}
      >
        {isInStock ? 'Add to Cart' : 'Out of Stock'}
      </AddToCartButton>
    </StyledCard>
  );
};

export default ProductCard;
