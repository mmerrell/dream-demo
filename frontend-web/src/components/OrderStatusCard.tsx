import React from 'react';
import {
  Card,
  CardContent,
  Box,
  Typography,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Chip,
  Button,
  Divider,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Avatar,
  LinearProgress,
  Fade,
} from '@mui/material';
import {
  CheckCircle,
  RadioButtonUnchecked,
  Schedule,
  LocalShipping,
  CreditCard,
  Inventory,
  Cancel,
  Error,
  LocalFlorist,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';

const OrderCard = styled(Card)(({ theme }) => ({
  marginBottom: theme.spacing(3),
  borderRadius: theme.spacing(2),
  boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
  border: '1px solid rgba(139, 195, 74, 0.1)',
  overflow: 'hidden',
  transition: 'all 0.3s ease',
  
  '&:hover': {
    boxShadow: '0 6px 30px rgba(139, 195, 74, 0.12)',
    transform: 'translateY(-2px)',
  },
}));

const OrderHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  padding: theme.spacing(2.5, 3),
  background: 'linear-gradient(135deg, rgba(139, 195, 74, 0.05) 0%, rgba(76, 175, 80, 0.02) 100%)',
  borderBottom: '1px solid rgba(139, 195, 74, 0.1)',
  
  [theme.breakpoints.down('sm')]: {
    flexDirection: 'column',
    alignItems: 'flex-start',
    gap: theme.spacing(1),
  },
}));

const OrderId = styled(Typography)(({ theme }) => ({
  fontFamily: "'Playfair Display', serif",
  fontWeight: 600,
  color: '#1B5E20',
  fontSize: '1.2rem',
}));

const OrderDate = styled(Typography)({
  color: '#4A5568',
  fontFamily: "'Inter', sans-serif",
  fontSize: '0.9rem',
});

const StatusChip = styled(Chip)<{ status: string }>(({ theme, status }) => {
  const getStatusStyles = () => {
    switch (status) {
      case 'pending':
        return {
          backgroundColor: 'rgba(255, 193, 7, 0.1)',
          color: '#E65100',
          border: '1px solid rgba(255, 193, 7, 0.3)',
        };
      case 'created':
        return {
          backgroundColor: 'rgba(33, 150, 243, 0.1)',
          color: '#0D47A1',
          border: '1px solid rgba(33, 150, 243, 0.3)',
        };
      case 'payment_confirmed':
        return {
          backgroundColor: 'rgba(139, 195, 74, 0.1)',
          color: '#1B5E20',
          border: '1px solid rgba(139, 195, 74, 0.3)',
        };
      case 'shipped':
        return {
          backgroundColor: 'rgba(103, 58, 183, 0.1)',
          color: '#4A148C',
          border: '1px solid rgba(103, 58, 183, 0.3)',
        };
      case 'delivered':
        return {
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          color: '#1B5E20',
          border: '1px solid rgba(76, 175, 80, 0.3)',
        };
      case 'cancelled':
        return {
          backgroundColor: 'rgba(244, 67, 54, 0.1)',
          color: '#C62828',
          border: '1px solid rgba(244, 67, 54, 0.3)',
        };
      case 'failed':
        return {
          backgroundColor: 'rgba(244, 67, 54, 0.1)',
          color: '#C62828',
          border: '1px solid rgba(244, 67, 54, 0.3)',
        };
      default:
        return {
          backgroundColor: 'rgba(158, 158, 158, 0.1)',
          color: '#424242',
          border: '1px solid rgba(158, 158, 158, 0.3)',
        };
    }
  };

  return {
    fontWeight: 600,
    textTransform: 'capitalize',
    borderRadius: theme.spacing(1.5),
    ...getStatusStyles(),
  };
});

const StyledStepper = styled(Stepper)(({ theme }) => ({
  '& .MuiStepLabel-root': {
    padding: theme.spacing(1, 0),
  },
  
  '& .MuiStepLabel-label': {
    fontFamily: "'Inter', sans-serif",
    fontWeight: 500,
    
    '&.Mui-completed': {
      color: '#2E7D32',
      fontWeight: 600,
    },
    
    '&.Mui-active': {
      color: '#1B5E20',
      fontWeight: 600,
    },
  },
  
  '& .MuiStepIcon-root': {
    color: 'rgba(139, 195, 74, 0.3)',
    
    '&.Mui-completed': {
      color: '#4CAF50',
    },
    
    '&.Mui-active': {
      color: '#8BC34A',
    },
  },
  
  '& .MuiStepConnector-line': {
    borderColor: 'rgba(139, 195, 74, 0.3)',
  },
  
  '& .MuiStepConnector-root.Mui-completed .MuiStepConnector-line': {
    borderColor: '#4CAF50',
  },
}));

const OrderItemsList = styled(List)(({ theme }) => ({
  padding: theme.spacing(1, 0),
}));

const OrderItemContainer = styled(ListItem)(({ theme }) => ({
  padding: theme.spacing(1, 0),
  borderBottom: '1px solid rgba(139, 195, 74, 0.08)',
  
  '&:last-child': {
    borderBottom: 'none',
  },
}));

const ItemImage = styled(Avatar)(({ theme }) => ({
  width: 50,
  height: 50,
  borderRadius: theme.spacing(1),
  border: '1px solid rgba(139, 195, 74, 0.1)',
}));

const TotalSection = styled(Box)(({ theme }) => ({
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  padding: theme.spacing(2),
  backgroundColor: 'rgba(139, 195, 74, 0.03)',
  borderRadius: theme.spacing(1.5),
  margin: theme.spacing(2, 0),
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
  fontSize: '1.3rem',
});

const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: theme.spacing(2),
  textTransform: 'none',
  fontWeight: 600,
  padding: theme.spacing(1, 3),
  
  '&.pay-button': {
    background: 'linear-gradient(135deg, #8BC34A 0%, #4CAF50 100%)',
    color: 'white',
    
    '&:hover': {
      background: 'linear-gradient(135deg, #7CB342 0%, #43A047 100%)',
    },
  },
  
  '&.cancel-button': {
    backgroundColor: 'rgba(244, 67, 54, 0.1)',
    color: '#C62828',
    border: '1px solid rgba(244, 67, 54, 0.3)',
    
    '&:hover': {
      backgroundColor: 'rgba(244, 67, 54, 0.15)',
    },
  },
}));

interface OrderItem {
  id: number;
  product_id: number;
  quantity: number;
  price_at_purchase: number;
  product: {
    id: number;
    name: string;
    image_url?: string;
  };
}

interface Order {
  id: number;
  created_at: string;
  status: string;
  items: OrderItem[];
}

interface OrderStatusCardProps {
  order: Order;
  onPayOrder?: (order: Order) => void;
  onCancelOrder?: (orderId: number) => void;
  loading?: boolean;
}

const orderSteps = [
  { label: 'Order Created', status: 'created', icon: <Schedule /> },
  { label: 'Payment Confirmed', status: 'payment_confirmed', icon: <CreditCard /> },
  { label: 'Preparing', status: 'packaging', icon: <Inventory /> },
  { label: 'Shipped', status: 'shipped', icon: <LocalShipping /> },
  { label: 'Delivered', status: 'delivered', icon: <CheckCircle /> },
];

const OrderStatusCard: React.FC<OrderStatusCardProps> = ({
  order,
  onPayOrder,
  onCancelOrder,
  loading = false,
}) => {
  const totalAmount = order.items.reduce(
    (sum, item) => sum + (Number(item.price_at_purchase) * item.quantity),
    0
  );

  const totalItems = order.items.reduce((sum, item) => sum + item.quantity, 0);

  const getActiveStep = () => {
    const statusMap: { [key: string]: number } = {
      'pending': 0,
      'created': 0,
      'payment_confirmed': 1,
      'packaging': 2,
      'shipped': 3,
      'delivered': 4,
      'cancelled': -1,
      'failed': -1,
    };
    
    return statusMap[order.status] || 0;
  };

  const canPay = order.status === 'pending' || order.status === 'created';
  const canCancel = ['pending', 'created', 'payment_confirmed'].includes(order.status);
  const isCompleted = order.status === 'delivered';
  const isCancelled = order.status === 'cancelled';
  const isFailed = order.status === 'failed';

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const activeStep = getActiveStep();

  return (
    <Fade in timeout={600}>
      <OrderCard>
        <OrderHeader>
          <Box>
            <OrderId>Order #{order.id}</OrderId>
            <OrderDate>{formatDate(order.created_at)}</OrderDate>
          </Box>
          <StatusChip label={order.status.replace('_', ' ')} status={order.status} />
        </OrderHeader>

        <CardContent sx={{ padding: 3 }}>
          {!isCancelled && !isFailed && (
            <Box sx={{ mb: 3 }}>
              <Typography
                variant="h6"
                sx={{
                  mb: 2,
                  fontFamily: "'Inter', sans-serif",
                  fontWeight: 600,
                  color: '#1B5E20',
                }}
              >
                Order Progress
              </Typography>
              
              <StyledStepper activeStep={activeStep} orientation="vertical">
                {orderSteps.map((step, index) => (
                  <Step key={step.label} completed={index < activeStep}>
                    <StepLabel
                      StepIconComponent={() => (
                        <Box sx={{ 
                          display: 'flex', 
                          alignItems: 'center',
                          color: index <= activeStep ? '#4CAF50' : 'rgba(139, 195, 74, 0.3)',
                        }}>
                          {index <= activeStep ? <CheckCircle /> : <RadioButtonUnchecked />}
                        </Box>
                      )}
                    >
                      {step.label}
                    </StepLabel>
                  </Step>
                ))}
              </StyledStepper>
              
              {activeStep >= 0 && activeStep < orderSteps.length - 1 && (
                <Box sx={{ mt: 2 }}>
                  <LinearProgress
                    variant="determinate"
                    value={(activeStep / (orderSteps.length - 1)) * 100}
                    sx={{
                      height: 6,
                      borderRadius: 3,
                      backgroundColor: 'rgba(139, 195, 74, 0.1)',
                      '& .MuiLinearProgress-bar': {
                        borderRadius: 3,
                        background: 'linear-gradient(90deg, #8BC34A, #4CAF50)',
                      },
                    }}
                  />
                </Box>
              )}
            </Box>
          )}

          <Typography
            variant="h6"
            sx={{
              mb: 2,
              fontFamily: "'Inter', sans-serif",
              fontWeight: 600,
              color: '#1B5E20',
            }}
          >
            Order Items ({totalItems})
          </Typography>

          <OrderItemsList>
            {order.items.map((item) => (
              <OrderItemContainer key={item.id}>
                <ListItemAvatar>
                  <ItemImage
                    src={item.product.image_url || '/api/placeholder/50/50'}
                    alt={item.product.name}
                  >
                    <LocalFlorist />
                  </ItemImage>
                </ListItemAvatar>
                <ListItemText
                  primary={
                    <Typography
                      variant="subtitle1"
                      sx={{
                        fontWeight: 600,
                        color: '#1B5E20',
                        fontFamily: "'Inter', sans-serif",
                      }}
                    >
                      {item.product.name}
                    </Typography>
                  }
                  secondary={
                    <Box sx={{ display: 'flex', gap: 2, mt: 0.5 }}>
                      <Typography variant="body2" color="text.secondary">
                        Quantity: {item.quantity}
                      </Typography>
                      <Typography
                        variant="body2"
                        sx={{
                          color: '#2E7D32',
                          fontWeight: 600,
                        }}
                      >
                        ${Number(item.price_at_purchase).toFixed(2)} each
                      </Typography>
                    </Box>
                  }
                />
                <Typography
                  variant="subtitle1"
                  sx={{
                    color: '#1B5E20',
                    fontWeight: 700,
                    fontFamily: "'Playfair Display', serif",
                  }}
                >
                  ${(Number(item.price_at_purchase) * item.quantity).toFixed(2)}
                </Typography>
              </OrderItemContainer>
            ))}
          </OrderItemsList>

          <TotalSection>
            <TotalLabel>Total</TotalLabel>
            <TotalAmount>${totalAmount.toFixed(2)}</TotalAmount>
          </TotalSection>

          {(canPay || canCancel) && (
            <Box sx={{ display: 'flex', gap: 2, mt: 2, justifyContent: 'flex-end' }}>
              {canCancel && onCancelOrder && (
                <ActionButton
                  className="cancel-button"
                  onClick={() => onCancelOrder(order.id)}
                  disabled={loading}
                  startIcon={<Cancel />}
                >
                  Cancel Order
                </ActionButton>
              )}
              {canPay && onPayOrder && (
                <ActionButton
                  className="pay-button"
                  variant="contained"
                  onClick={() => onPayOrder(order)}
                  disabled={loading}
                  startIcon={<CreditCard />}
                >
                  {loading ? 'Processing...' : 'Pay Now'}
                </ActionButton>
              )}
            </Box>
          )}
        </CardContent>
      </OrderCard>
    </Fade>
  );
};

export default OrderStatusCard;
