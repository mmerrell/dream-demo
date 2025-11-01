import React, { useState } from 'react';
import { CardElement, useStripe, useElements } from '@stripe/react-stripe-js';
import Button from '@mui/material/Button';

interface PaymentFormProps {
    clientSecret: string;
    onSuccess: () => void;
    onCancel: () => void;
}

const PaymentForm: React.FC<PaymentFormProps> = ({ clientSecret, onSuccess, onCancel }) => {
    const stripe = useStripe();
    const elements = useElements();
    const [isProcessing, setIsProcessing] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const CARD_ELEMENT_OPTIONS = {
        style: {
            base: {
                fontSize: '16px',
                color: '#32325d',
                fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
                '::placeholder': {
                    color: '#aab7c4',
                },
                padding: '12px',
            },
            invalid: {
                color: '#fa755a',
                iconColor: '#fa755a',
            },
        },
    };

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();

        if (!stripe || !elements) {
            return;
        }

        setIsProcessing(true);
        setError(null);

        const { error, paymentIntent } = await stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: elements.getElement(CardElement)!,
            },
        });

        if (error) {
            setError(error.message || 'An unexpected error occurred.');
            setIsProcessing(false);
        } else if (paymentIntent && paymentIntent.status === 'succeeded') {
            onSuccess();
            setIsProcessing(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="payment-form" aria-label="Payment form">
            <div style={{ 
                padding: '12px', 
                border: '1px solid #ccc', 
                borderRadius: '4px',
                backgroundColor: '#fff'
            }}>
                <CardElement options={CARD_ELEMENT_OPTIONS} />
            </div>
            
            {error && (
                <div style={{ color: '#fa755a', fontSize: '14px' }}
                    role="alert"
                    aria-live="polite"
                >
                    {error}
                </div>
            )}
            
            <div className="payment-buttons">
                <Button
                    type="submit"
                    variant="contained"
                    color="primary"
                    fullWidth
                    disabled={isProcessing || !stripe || !elements}
                    aria-label="Submit payment"
                >
                    {isProcessing ? "Processing..." : "Pay"}
                </Button>
                <Button
                    type="button"
                    variant="outlined"
                    color="secondary"
                    fullWidth
                    onClick={onCancel}
                    disabled={isProcessing}
                    aria-label="Cancel payment"
                >
                    Cancel
                </Button>
            </div>
        </form>
    );
};

export default PaymentForm;