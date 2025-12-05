// frontend-web/src/components/ErrorBoundary.tsx
import React from 'react';
import { Alert, Box, Button, Typography } from '@mui/material';
import { Refresh, BugReport } from '@mui/icons-material';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: React.ErrorInfo;
  errorId?: string;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
  sprintVersion?: string;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    const errorId = `fe_err_${Date.now()}`;

    this.setState({ error, errorInfo, errorId });

    // Send to Backtrace if configured
    this.sendErrorToBacktrace(error, errorInfo, errorId);
  }

  sendErrorToBacktrace(error: Error, errorInfo: React.ErrorInfo, errorId: string) {
    const errorData = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      errorId,
      sprintVersion: this.props.sprintVersion || 'unknown',
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    };

    // For now, just log - implement Backtrace API call later
    console.error('Frontend Error:', errorData);

    // Future: Send to Backtrace
    // fetch('/api/frontend-error', { method: 'POST', body: JSON.stringify(errorData) });
  }

  render() {
    if (this.state.hasError) {
      return (
        <Box sx={{ p: 3, textAlign: 'center' }}>
          <Alert severity="error" sx={{ mb: 2 }}>
            <Typography variant="h6" gutterBottom>
              🌪️ Something went wrong in {this.props.sprintVersion || 'the app'}
            </Typography>
            <Typography variant="body2" sx={{ mb: 2 }}>
              Error ID: {this.state.errorId}
            </Typography>
            <Button
              variant="contained"
              startIcon={<Refresh />}
              onClick={() => window.location.reload()}
              sx={{ mr: 1 }}
            >
              Refresh Page
            </Button>
            <Button
              variant="outlined"
              startIcon={<BugReport />}
              onClick={() => console.log('Report error:', this.state)}
            >
              Report Bug
            </Button>
          </Alert>

          {process.env.NODE_ENV === 'development' && (
            <Box sx={{ textAlign: 'left', backgroundColor: '#f5f5f5', p: 2, borderRadius: 1 }}>
              <Typography variant="caption" component="pre">
                {this.state.error?.stack}
              </Typography>
            </Box>
          )}
        </Box>
      );
    }

    return this.props.children;
  }
}
