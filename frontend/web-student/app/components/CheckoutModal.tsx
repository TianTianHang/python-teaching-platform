
import { useEffect, useState } from 'react';
import {
  Modal,
  Box,
  Typography,
  Radio,
  RadioGroup,
  FormControlLabel,
  Button,
  Divider,
  IconButton,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import type { MembershipType } from '~/types/user';
import { showNotification } from './Notification';
import { useFetcher } from 'react-router';
import type { Order } from '~/types/order';

const style = {
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: { xs: '90%', sm: 400 },
  bgcolor: 'background.paper',
  borderRadius: 2,
  boxShadow: 24,
  p: 3,
};

export default function CheckoutModal({ open, onClose, membershipType }: { open: boolean, onClose: () => void, membershipType: MembershipType | null }) {
  const [paymentMethod, setPaymentMethod] = useState('alipay'); // 默认支付宝
  const pay = useFetcher<{
    method: string;
    pay_url: string;
    gateway: string;
  }>()
  const order = useFetcher<Order>()
  if (!membershipType) return null;

  const handleOrderCreate = () => {
    // 这里可以调用创建订单 + 跳转支付接口
    console.log('选择的支付方式:', paymentMethod);
    console.log('支付金额:', membershipType.price);

    showNotification("success", "创建订单", "正在创建订单")
    order.submit({ membershipType: membershipType.id }, {
      method: "post",
      action: "/orders/create"
    })


  };
  useEffect(() => {
    if (order.state == "idle" && order.data) {
      showNotification("success", "订单创建成功", `订单号：${order.data?.order_number}`)
      pay.submit({ order_number: order.data.order_number, payment_method: paymentMethod }, {
        method: "post",
        action: "/payment/pay"
      })

    }
  }, [order.state])
  useEffect(() => {
    if (pay.state == "idle" && pay.data) {
      console.log(pay.data.pay_url)
      window.location.href = pay.data.pay_url;
      onClose();
    }
  }, [pay.state])
  return (
    <Modal
      open={open}
      onClose={onClose}
      aria-labelledby="checkout-modal-title"
      aria-describedby="checkout-modal-description"
    >
      <Box sx={style}>
        {/* 标题栏 */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography id="checkout-modal-title" variant="h6" fontWeight="bold">
            确认支付
          </Typography>
          <IconButton size="small" onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>

        <Divider sx={{ mb: 2 }} />

        {/* 订阅信息 */}
        <Box mb={2}>
          <Typography variant="body1" color="text.secondary">
            会员类型
          </Typography>
          <Typography variant="h6" fontWeight="medium">
            {membershipType.name}
          </Typography>
        </Box>

        {/* 金额 */}
        <Box mb={3} textAlign="center">
          <Typography variant="h4" color="primary" fontWeight="bold">
            ¥{membershipType.price}
          </Typography>
        </Box>

        {/* 支付方式 */}
        <Box mb={3}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            请选择支付方式
          </Typography>
          <RadioGroup
            value={paymentMethod}
            onChange={(e) => setPaymentMethod(e.target.value)}
            row
            sx={{ justifyContent: 'center' }}
          >
            <FormControlLabel
              value="alipay"
              control={<Radio />}
              label={
                <Box display="flex" alignItems="center">
                  <img
                    src="https://gw.alipayobjects.com/zos/rmsportal/KDpgvguMpGfqaHPjicRK.svg"
                    alt="Alipay"
                    style={{ height: 24, marginRight: 8 }}
                  />
                  支付宝
                </Box>
              }
            />
            <FormControlLabel
              value="wechat"
              control={<Radio />}
              label={
                <Box display="flex" alignItems="center">
                  <img
                    src="https://res.wx.qq.com/op_res/YNLrGQ7qy5iSdJZqXHbNwVxTlBzKkFmUeXaYvZ9qQw"
                    alt="WeChat Pay"
                    style={{ height: 24, marginRight: 8 }}
                  />
                  微信
                </Box>
              }
            />
          </RadioGroup>
        </Box>

        {/* 操作按钮 */}
        <Button
          fullWidth
          variant="contained"
          color="primary"
          size="large"
          startIcon={<AccountBalanceWalletIcon />}
          onClick={handleOrderCreate}
        >
          结账
        </Button>

        <Typography variant="caption" color="text.secondary" textAlign="center" mt={2}>
          支付安全由第三方平台保障
        </Typography>
      </Box>
    </Modal>
  );
}