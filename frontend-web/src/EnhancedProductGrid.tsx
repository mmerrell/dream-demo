import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Typography,
  Box,
  Fade,
  CircularProgress,
  Alert,
  TextField,
  InputAdornment,
  Chip,
  Stack,
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import ProductCard from './components/ProductCard';

const StyledContainer = styled(Container)(({ theme }) => ({
  paddingTop: theme.spacing(4),
  paddingBottom: theme.spacing(6),
  position: 'relative',
  
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: '60px',
    background: 'linear-gradient(135deg, rgba(139, 195, 74, 0.03) 0%, rgba(76, 175, 80, 0.02) 100%)',
    borderRadius: '0 0 24px 24px',
  },
}));

const HeaderSection = styled(Box)(({ theme }) => ({
  textAlign: 'center',
  marginBottom: theme.spacing(4),
  position: 'relative',
  zIndex: 1,
}));

const Title = styled(Typography)<{ component?: React.ElementType }>(({ theme }) => ({
  fontFamily: "'Playfair Display', serif",
  fontWeight: 600,
  color: '#1B5E20',
  marginBottom: theme.spacing(1),
  position: 'relative',
  
  '&::after': {
    content: '""',
    position: 'absolute',
    bottom: '-8px',
    left: '50%',
    transform: 'translateX(-50%)',
    width: '60px',
    height: '3px',
    background: 'linear-gradient(90deg, #8BC34A, #4CAF50)',
    borderRadius: '2px',
  },
}));

const Subtitle = styled(Typography)<{ component?: React.ElementType }>(({ theme }) => ({
  color: '#4A5568',
  fontFamily: "'Inter', sans-serif",
  fontSize: '1.1rem',
  fontWeight: 400,
  lineHeight: 1.5,
}));

const SearchAndFilterSection = styled(Box)(({ theme }) => ({
  display: 'flex',
  gap: theme.spacing(2),
  marginBottom: theme.spacing(4),
  flexWrap: 'wrap',
  alignItems: 'center',
  justifyContent: 'space-between',
  
  [theme.breakpoints.down('md')]: {
    flexDirection: 'column',
    alignItems: 'stretch',
  },
}));

const SearchField = styled(TextField)(({ theme }) => ({
  minWidth: '300px',
  flex: 1,
  maxWidth: '400px',
  
  '& .MuiOutlinedInput-root': {
    borderRadius: theme.spacing(3),
    backgroundColor: 'rgba(255, 255, 255, 0.8)',
    backdropFilter: 'blur(10px)',
    border: '1px solid rgba(139, 195, 74, 0.2)',
    
    '&:hover': {
      borderColor: 'rgba(139, 195, 74, 0.4)',
    },
    
    '&.Mui-focused': {
      borderColor: '#8BC34A',
      boxShadow: '0 0 0 2px rgba(139, 195, 74, 0.1)',
    },
  },
  
  [theme.breakpoints.down('md')]: {
    minWidth: 'unset',
    maxWidth: 'unset',
  },
}));

const FilterChips = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'row',
  gap: theme.spacing(1),
  flexWrap: 'wrap',
  
  [theme.breakpoints.down('md')]: {
    justifyContent: 'center',
  },
}));

const FilterChip = styled(Chip)<{ active: boolean }>(({ theme, active }) => ({
  fontWeight: 500,
  borderRadius: theme.spacing(2),
  transition: 'all 0.2s ease',
  cursor: 'pointer',
  
  ...(active && {
    backgroundColor: '#8BC34A',
    color: 'white',
    
    '&:hover': {
      backgroundColor: '#7CB342',
    },
  }),
  
  ...(!active && {
    backgroundColor: 'rgba(139, 195, 74, 0.08)',
    color: '#2E7D32',
    border: '1px solid rgba(139, 195, 74, 0.2)',
    
    '&:hover': {
      backgroundColor: 'rgba(139, 195, 74, 0.15)',
      borderColor: 'rgba(139, 195, 74, 0.4)',
    },
  }),
}));

const LoadingContainer = styled(Box)({
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  height: '300px',
});

const ProductGrid = styled(Grid)(({ theme }) => ({
  marginTop: theme.spacing(2),
  
  '& .MuiGrid-item': {
    display: 'flex',
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

interface ProductGridProps {
  products: Product[];
  loading?: boolean;
  error?: string;
  onAddToCart: (product: Product) => void;
}

const filters = [
  { id: 'all', label: 'All Flowers', value: 'all' },
  { id: 'roses', label: 'Roses', value: 'rose' },
  { id: 'tulips', label: 'Tulips', value: 'tulip' },
  { id: 'sunflowers', label: 'Sunflowers', value: 'sunflower' },
  { id: 'in-stock', label: 'In Stock', value: 'in-stock' },
];

const EnhancedProductGrid: React.FC<ProductGridProps> = ({
  products,
  loading = false,
  error,
  onAddToCart,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilter, setActiveFilter] = useState('all');
  const [filteredProducts, setFilteredProducts] = useState<Product[]>(products);

  useEffect(() => {
    let filtered = products;

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(product =>
        product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (product.description && product.description.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }

    // Apply category filter
    if (activeFilter !== 'all') {
      if (activeFilter === 'in-stock') {
        filtered = filtered.filter(product => product.inventory_count > 0);
      } else {
        filtered = filtered.filter(product =>
          product.name.toLowerCase().includes(activeFilter.toLowerCase())
        );
      }
    }

    setFilteredProducts(filtered);
  }, [products, searchTerm, activeFilter]);

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };

  const handleFilterClick = (filterValue: string) => {
    setActiveFilter(filterValue);
  };

  if (error) {
    return (
      <StyledContainer maxWidth="lg">
        <Alert 
          severity="error" 
          sx={{ 
            mt: 4,
            borderRadius: 2,
            '& .MuiAlert-message': {
              fontSize: '1rem',
            },
          }}
        >
          {error}
        </Alert>
      </StyledContainer>
    );
  }

  return (
    <StyledContainer maxWidth="lg">
      <HeaderSection>
        <Fade in timeout={800}>
          <div>
            <Title variant="h3" component="h1">
              Fresh Flowers
            </Title>
            <Subtitle variant="h6" component="p">
              Beautiful blooms delivered fresh to your door
            </Subtitle>
          </div>
        </Fade>
      </HeaderSection>

      <SearchAndFilterSection>
        <SearchField
          placeholder="Search flowers..."
          value={searchTerm}
          onChange={handleSearchChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ color: '#8BC34A' }} />
              </InputAdornment>
            ),
          }}
        />
        
        <FilterChips>
          {filters.map((filter) => (
            <FilterChip
              key={filter.id}
              label={filter.label}
              active={activeFilter === filter.value}
              onClick={() => handleFilterClick(filter.value)}
            />
          ))}
        </FilterChips>
      </SearchAndFilterSection>

      {loading ? (
        <LoadingContainer>
          <CircularProgress 
            size={60} 
            sx={{ 
              color: '#8BC34A',
              '& .MuiCircularProgress-circle': {
                strokeLinecap: 'round',
              },
            }} 
          />
        </LoadingContainer>
      ) : (
        <Fade in timeout={1000}>
          <ProductGrid container spacing={3}>
            {filteredProducts.length > 0 ? (
              filteredProducts.map((product, index) => (
                <Grid 
                  item 
                  xs={12} 
                  sm={6} 
                  md={4} 
                  lg={3} 
                  key={product.id}
                  sx={{
                    '& > *': {
                      width: '100%',
                    },
                  }}
                >
                  <Fade in timeout={600 + (index * 100)}>
                    <div style={{ width: '100%' }}>
                      <ProductCard
                        product={product}
                        onAddToCart={onAddToCart}
                      />
                    </div>
                  </Fade>
                </Grid>
              ))
            ) : (
              <Grid item xs={12}>
                <Box sx={{ textAlign: 'center', py: 8 }}>
                  <Typography 
                    variant="h6" 
                    color="text.secondary"
                    sx={{ 
                      fontFamily: "'Inter', sans-serif",
                      mb: 1,
                    }}
                  >
                    No flowers found
                  </Typography>
                  <Typography 
                    variant="body2" 
                    color="text.secondary"
                  >
                    Try adjusting your search or filter criteria
                  </Typography>
                </Box>
              </Grid>
            )}
          </ProductGrid>
        </Fade>
      )}
    </StyledContainer>
  );
};

export default EnhancedProductGrid;
