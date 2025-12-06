import React from 'react';
import {
  Drawer,
  Box,
  Typography,
  IconButton,
  Divider,
  Button,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Avatar,
  Badge,
  Chip,
  Fade,
  Slide,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Close as CloseIcon,
  Add as AddIcon,
  Remove as RemoveIcon,
  Delete as DeleteIcon,
  ShoppingCart as CartIcon,
  LocalFlorist as FlowerIcon,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';

const StyledDrawer = styled(Drawer)(({ theme }) => ({
  '& .MuiDrawer-paper': {
    width: 420,
    maxWidth: '90vw',
    background: 'linear-gradient(135deg, #ffffff 0%, #f8fffe 100%)',
    borderLeft: '1px solid rgba(139, 195, 74, 0.1)',
    borderTopLeftRadius: theme.spacing(3),
    borderBottomLeftRadius: theme.spacing(3),
    boxShadow: '0 16px 40px rgba(0,0,0,0.12)',
    overflow: 'hidden',
    
    [theme.breakpoints.down('sm')]: {
      width: '100vw',
      maxWidth: '100vw',
      borderRadius: 0,
    },
  },
}));

const CartHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(2.5, 3),
  background: 'linear-gradient(135deg, rgba(139, 195, 74, 0.05) 0%, rgba(76, 175, 80, 0.03) 100%)',
  borderBottom: '1px solid rgba(139, 195, 74, 0.1)',
  position: 'relative',
  
  '&::after': {
    content: '""',
    position: 'absolute',
    bottom: 0,
    left: '50%',
    transform: 'translateX(-50%)',
    width: '60px',
    height: '2px',
    background: 'linear-gradient(90deg, #8BC34A, #4CAF50)',
    borderRadius: '1px',
  },
}));

const CartTitle = styled(Typography)(({ theme }) => ({
  fontFamily: "'Playfair Display', serif",
  fontWeight: 600,
  color: '#1B5E20',
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1.5),
}));

const CartContent = styled(Box)(({ theme }) => ({
  flex: 1,
  display: 'flex',
  flexDirection: 'column',
  height: 'calc(100vh - 140px)',
  position: 'relative',
}));

const CartItems = styled(List)(({ theme }) => ({
  flex: 1,
  padding: theme.spacing(1, 0),
  overflow: 'auto',
  
  '&::-webkit-scrollbar': {
    width: '6px',
  },
  
  '&::-webkit-scrollbar-track': {
    background: 'rgba(139, 195, 74, 0.05)',
    borderRadius: '3px',
  },
  
  '&::-webkit-scrollbar-thumb': {
    background: 'rgba(139, 195, 74, 0.3)',
    borderRadius: '3px',
    
    '&:hover': {
      background: 'rgba(139, 195, 74, 0.5)',
    },
  },
}));

const CartItemContainer = styled(ListItem)(({ theme }) => ({
  padding: theme.spacing(2, 3),
  borderBottom: '1px solid rgba(139, 195, 74, 0.08)',
  transition: 'all 0.2s ease',
  
  '&:hover': {
    backgroundColor: 'rgba(139, 195, 74, 0.02)',
  },
}));

const ItemImage = styled(Avatar)(({ theme }) => ({
  width: 64,
  height: 64,
  borderRadius: theme.spacing(1.5),
  border: '2px solid rgba(139, 195, 74, 0.1)',
}));

const QuantityControls = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1),
  marginTop: theme.spacing(1),
}));

const QuantityButton = styled(IconButton)(({ theme }) => ({
  width: 32,
  height: 32,
  backgroundColor: 'rgba(139, 195, 74, 0.1)',
  color: '#2E7D32',
  border: '1px solid rgba(139, 195, 74, 0.2)',
  
  '&:hover': {
    backgroundColor: '#8BC34A',
    color: 'white',
    borderColor: '#8BC34A',
  },
  
  '&:disabled': {
    backgroundColor: 'rgba(0,0,0,0.04)',
    color: 'rgba(0,0,0,0.26)',
    borderColor: 'rgba(0,0,0,0.08)',
  },
}));

const CartFooter = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2.5, 3, 3),
  borderTop: '1px solid rgba(139, 195, 74, 0.1)',
  background: 'linear-gradient(135deg, rgba(139, 195, 74, 0.02) 0%, rgba(76, 175, 80, 0.01) 100%)',
}));

const TotalSection = styled(Box)(({ theme }) => ({
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: theme.spacing(2.5),
  padding: theme.spacing(2),
  backgroundColor: 'rgba(139, 195, 74, 0.05)',
  borderRadius: theme.spacing(2),
  border: '1px solid rgba(139, 195, 74, 0.1)',
}));

const TotalLabel = styled(Typography)({
  fontFamily: "'Inter', sans-serif",
  fontWeight: 600,
  color: '#2E7D32',
  fontSize: '1.1rem',
});

const TotalAmount = styled(Typography)({
  fontFamily: "'Playfair Display', serif",
  fontWeight: 700,
  color: '#1B5E20',
  fontSize: '1.5rem',
});

const CheckoutButton = styled(Button)(({ theme }) => ({
  width: '100%',
  padding: theme.spacing(1.5),
  borderRadius: theme.spacing(3),
  textTransform: 'none',
  fontSize: '1.1rem',
  fontWeight: 600,
  background: 'linear-gradient(135deg, #8BC34A 0%, #4CAF50 100%)',
  color: 'white',
  border: 'none',
  boxShadow: '0 6px 20px rgba(139, 195, 74, 0.3)',
  
  '&:hover': {
    background: 'linear-gradient(135deg, #7CB342 0%, #43A047 100%)',
    boxShadow: '0 8px 25px rgba(139, 195, 74, 0.4)',
    transform: 'translateY(-1px)',
  },
  
  '&:active': {
    transform: 'translateY(0)',
  },
}));

const EmptyCartContainer = styled(Box)(({ theme }) => ({
  flex: 1,
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  padding: theme.spacing(4),
  textAlign: 'center',
}));

const EmptyCartIcon = styled(FlowerIcon)(({ theme }) => ({
  fontSize: '4rem',
  color: 'rgba(139, 195, 74, 0.3)',
  marginBottom: theme.spacing(2),
}));

interface CartItem {
  id: number;
  name: string;
  price: number;
  quantity: number;
  image_url?: string | null;
}

interface ShoppingCartDrawerProps {
  open: boolean;
  onClose: () => void;
  items: CartItem[];
  onUpdateQuantity: (id: number, quantity: number) => void;
  onRemoveItem: (id: number) => void;
  onCheckout: () => void;
  loading?: boolean;
}

const ShoppingCartDrawer: React.FC<ShoppingCartDrawerProps> = ({
  open,
  onClose,
  items,
  onUpdateQuantity,
  onRemoveItem,
  onCheckout,
  loading = false,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const totalItems = items.reduce((sum, item) => sum + item.quantity, 0);
  const totalAmount = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);

  const handleQuantityChange = (id: number, delta: number) => {
    const item = items.find(i => i.id === id);
    if (item) {
      const newQuantity = Math.max(0, item.quantity + delta);
      if (newQuantity === 0) {
        onRemoveItem(id);
      } else {
        onUpdateQuantity(id, newQuantity);
      }
    }
  };

  return (
    <StyledDrawer
      anchor="right"
      open={open}
      onClose={onClose}
      transitionDuration={400}
    >
      <CartHeader>
        <CartTitle variant="h6">
          <Badge badgeContent={totalItems} color="primary" max={99}>
            <CartIcon />
          </Badge>
          Shopping Cart
        </CartTitle>
        <IconButton 
          onClick={onClose}
          sx={{ 
            color: '#2E7D32',
            '&:hover': { 
              backgroundColor: 'rgba(139, 195, 74, 0.1)',
            },
          }}
        >
          <CloseIcon />
        </IconButton>
      </CartHeader>

      <CartContent>
        {items.length === 0 ? (
          <EmptyCartContainer>
            <Fade in timeout={600}>
              <div>
                <EmptyCartIcon />
                <Typography 
                  variant="h6" 
                  color="text.secondary"
                  sx={{ 
                    fontFamily: "'Playfair Display', serif",
                    mb: 1,
                  }}
                >
                  Your cart is empty
                </Typography>
                <Typography 
                  variant="body2" 
                  color="text.secondary"
                  sx={{ fontFamily: "'Inter', sans-serif" }}
                >
                  Add some beautiful flowers to get started
                </Typography>
              </div>
            </Fade>
          </EmptyCartContainer>
        ) : (
          <>
            <CartItems>
              {items.map((item, index) => (
                <Slide
                  key={item.id}
                  direction="left"
                  in={true}
                  timeout={300 + (index * 100)}
                >
                  <CartItemContainer>
                    <ListItemAvatar>
                      <ItemImage
                        src={item.image_url || '/api/placeholder/64/64'}
                        alt={item.name}
                      />
                    </ListItemAvatar>
                    
                    <ListItemText
                      primary={
                        <Typography
                          variant="subtitle1"
                          sx={{
                            fontWeight: 600,
                            color: '#1B5E20',
                            fontFamily: "'Inter', sans-serif",
                            lineHeight: 1.3,
                          }}
                        >
                          {item.name}
                        </Typography>
                      }
                      secondary={
                        <Box>
                          <Typography
                            variant="body1"
                            sx={{
                              color: '#2E7D32',
                              fontWeight: 600,
                              fontFamily: "'Playfair Display', serif",
                              fontSize: '1.1rem',
                              mt: 0.5,
                            }}
                          >
                            ${item.price.toFixed(2)} each
                          </Typography>
                          
                          <QuantityControls>
                            <QuantityButton
                              size="small"
                              onClick={() => handleQuantityChange(item.id, -1)}
                            >
                              <RemoveIcon fontSize="small" />
                            </QuantityButton>
                            
                            <Chip
                              label={item.quantity}
                              size="small"
                              sx={{
                                fontWeight: 600,
                                backgroundColor: 'rgba(139, 195, 74, 0.1)',
                                color: '#2E7D32',
                                border: '1px solid rgba(139, 195, 74, 0.2)',
                                minWidth: '50px',
                              }}
                            />
                            
                            <QuantityButton
                              size="small"
                              onClick={() => handleQuantityChange(item.id, 1)}
                            >
                              <AddIcon fontSize="small" />
                            </QuantityButton>
                            
                            <IconButton
                              size="small"
                              onClick={() => onRemoveItem(item.id)}
                              sx={{
                                ml: 1,
                                color: '#D32F2F',
                                '&:hover': {
                                  backgroundColor: 'rgba(211, 47, 47, 0.1)',
                                },
                              }}
                            >
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </QuantityControls>
                        </Box>
                      }
                    />
                  </CartItemContainer>
                </Slide>
              ))}
            </CartItems>

            <CartFooter>
              <TotalSection>
                <TotalLabel>Total ({totalItems} items)</TotalLabel>
                <TotalAmount>${totalAmount.toFixed(2)}</TotalAmount>
              </TotalSection>
              
              <CheckoutButton
                variant="contained"
                onClick={onCheckout}
                disabled={loading || items.length === 0}
                startIcon={loading ? undefined : <CartIcon />}
              >
                {loading ? 'Processing...' : 'Proceed to Checkout'}
              </CheckoutButton>
            </CartFooter>
          </>
        )}
      </CartContent>
    </StyledDrawer>
  );
};

export default ShoppingCartDrawer;
