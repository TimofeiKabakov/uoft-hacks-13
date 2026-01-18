/**
 * Loan Amount Step
 *
 * Step to collect the loan amount requested by the user.
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { ArrowLeft, ArrowRight, DollarSign } from 'lucide-react';

interface LoanAmountStepProps {
  initialAmount?: number;
  onSubmit: (amount: number) => void;
  onBack: () => void;
}

export function LoanAmountStep({ initialAmount = 10000, onSubmit, onBack }: LoanAmountStepProps) {
  const [loanAmount, setLoanAmount] = useState<string>(initialAmount.toString());
  const [error, setError] = useState<string>('');

  const formatCurrency = (value: string): string => {
    // Remove non-numeric characters
    const numeric = value.replace(/[^0-9]/g, '');

    if (!numeric) return '';

    // Format with commas
    return parseInt(numeric).toLocaleString('en-US');
  };

  const handleAmountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const numeric = value.replace(/[^0-9]/g, '');

    if (numeric) {
      const amount = parseInt(numeric);
      if (amount > 10000000) {
        setError('Loan amount cannot exceed $10,000,000');
        return;
      }
    }

    setError('');
    setLoanAmount(numeric);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const amount = parseInt(loanAmount.replace(/[^0-9]/g, ''));

    if (!amount || isNaN(amount)) {
      setError('Please enter a valid loan amount');
      return;
    }

    if (amount < 1000) {
      setError('Minimum loan amount is $1,000');
      return;
    }

    if (amount > 10000000) {
      setError('Maximum loan amount is $10,000,000');
      return;
    }

    setError('');
    onSubmit(amount);
  };

  const displayAmount = loanAmount ? formatCurrency(loanAmount) : '';

  return (
    <Card className="p-8 bg-card/50 backdrop-blur border-border/50">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        <div className="mb-8">
          <h2 className="text-3xl font-bold mb-2">Loan Amount</h2>
          <p className="text-muted-foreground">
            How much funding are you requesting?
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="loanAmount">Requested Loan Amount</Label>
            <div className="relative">
              <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
              <Input
                id="loanAmount"
                type="text"
                placeholder="10,000"
                value={displayAmount}
                onChange={handleAmountChange}
                className="pl-10 text-lg h-12"
                autoFocus
              />
            </div>
            {error && (
              <p className="text-sm text-destructive">{error}</p>
            )}
            <p className="text-xs text-muted-foreground">
              Enter an amount between $1,000 and $10,000,000
            </p>
          </div>

          <div className="grid grid-cols-3 gap-3">
            {[5000, 10000, 25000, 50000, 100000, 250000].map((amount) => (
              <Button
                key={amount}
                type="button"
                variant="outline"
                size="sm"
                onClick={() => {
                  setLoanAmount(amount.toString());
                  setError('');
                }}
                className="text-xs"
              >
                ${(amount / 1000).toFixed(0)}K
              </Button>
            ))}
          </div>

          <div className="flex justify-between pt-4">
            <Button type="button" variant="ghost" onClick={onBack}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Button>
            <Button type="submit" className="min-w-32">
              Continue
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </form>
      </motion.div>
    </Card>
  );
}
