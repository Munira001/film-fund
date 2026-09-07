import * as React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cn } from '@/lib/utils';
import { cva, type VariantProps } from 'class-variance-authority';

const buttonVariants = cva(
  'pressable inline-flex items-center justify-center gap-2 whitespace-nowrap text-sm font-semibold tracking-[-0.5px] transition-[transform,opacity,color,background-color,box-shadow,border-color] duration-150 ease-[cubic-bezier(0,0,0.2,1)] focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50 disabled:hover:transform-none [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0',
  {
    variants: {
      variant: {
        default:
          'rounded-2xl bg-foreground text-background hover:opacity-90',
        destructive:
          'rounded-2xl bg-destructive text-destructive-foreground hover:opacity-90',
        outline:
          'rounded-3xl border border-border bg-background hover:bg-muted/60',
        secondary:
          'rounded-2xl border border-border bg-card hover:bg-muted/60',
        ghost:
          'rounded-2xl border border-transparent bg-transparent hover:border-border hover:bg-muted/60',
        link: 'rounded-none text-foreground underline-offset-4 hover:underline',
      },
      size: {
        default: 'h-9 px-4 py-2',
        sm: 'h-8 px-3 text-sm',
        lg: 'h-12 px-6',
        icon: 'h-9 w-9 rounded-2xl',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button';
    return (
      <Comp
        className={cn(buttonVariants({ variant, size }), className)}
        ref={ref}
        {...props}
      />
    );
  },
);
Button.displayName = 'Button';

export { Button, buttonVariants };
