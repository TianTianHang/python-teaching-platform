import { TextField, type TextFieldProps } from '@mui/material';
import { forwardRef } from 'react';

export type FormTextFieldProps = Omit<TextFieldProps, 'variant'>;
/**
 * 统一的表单字段组件
 *
 * 封装了认证页面中 TextField 的重复样式配置，包括：
 * - 统一的输入框样式 (悬停和聚焦时的下划线颜色)
 * - 统一的标签样式
 * - 使用主题颜色自动适配深色/浅色模式
 *
 * @example
 * <FormTextField
 *   margin="normal"
 *   required
 *   fullWidth
 *   label="用户名"
 *   name="username"
 *   autoComplete="username"
 *   autoFocus
 * />
 */
export const FormTextField = forwardRef<HTMLDivElement, FormTextFieldProps>(
  (props, ref) => {
    const { slotProps, ...rest } = props;

    // 统一的 slotProps 配置，消除重复代码
    const defaultSlotProps = {
      input: {
        sx: {
          color: 'text.primary',
          // 悬停时的下划线颜色
          '&:hover': {
            '&:not(.Mui-disabled):before': {
              borderBottomColor: 'primary.main',
            },
          },
          // 聚焦时的下划线颜色
          '&.Mui-focused': {
            '&:before': {
              borderBottomColor: 'primary.main',
            },
          },
        },
      },
      inputLabel: {
        sx: {
          color: 'text.primary',
        },
      },
    };

    return (
      <TextField
        ref={ref}
        variant="filled"
        slotProps={slotProps || defaultSlotProps}
        {...rest}
      />
    );
  }
);

FormTextField.displayName = 'FormTextField';