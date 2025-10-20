import * as React from 'react';
import Snackbar from '@mui/material/Snackbar';
import MuiAlert, { type AlertProps } from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';

// 为了避免与HTML元素Alert冲突，我们将MuiAlert重命名
const Alert = React.forwardRef<HTMLDivElement, AlertProps>(function Alert(
  props,
  ref,
) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

interface NotificationState {
  open: boolean;
  type: 'error' | 'warning' | 'success' | 'info';
  title: string;
  message: string;
}

let setNotificationState: React.Dispatch<React.SetStateAction<NotificationState>> | null = null;

const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [notification, setNotification] = React.useState<NotificationState>({
    open: false,
    type: 'success',
    title: '',
    message: '',
  });

  setNotificationState = setNotification;

  const handleClose = (event?: React.SyntheticEvent | Event, reason?: string) => {
    if (reason === 'clickaway') {
      return;
    }
    setNotification((prev) => ({ ...prev, open: false }));
  };

  return (
    <>
      {children}
      <Snackbar open={notification.open} autoHideDuration={6000} onClose={handleClose}>
        <Alert onClose={handleClose} severity={notification.type} sx={{ width: '100%' }}>
          {notification.title && <AlertTitle>{notification.title}</AlertTitle>}
          {notification.message}
        </Alert>
      </Snackbar>
    </>
  );
};

const showNotification = (type: 'error' | 'warning' | 'success', title: string, message: string) => {
  if (setNotificationState) {
    setNotificationState({
      open: true,
      type: type, // MUI Alert的severity prop与你的type匹配
      title: title,
      message: message,
    });
  } else {
    console.error("NotificationProvider is not rendered. Unable to show notification.");
  }
};

export { showNotification, NotificationProvider };
